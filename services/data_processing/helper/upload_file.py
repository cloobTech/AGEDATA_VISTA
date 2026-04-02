import cloudinary
from celery_app import celery_app
import cloudinary.uploader
from sqlalchemy.orm import Session
from io import BytesIO
from errors.exceptions import EntityNotFoundError
from services.data_processing.helper.clean_file import clean_file_with_pandas
from services.data_processing.user_files.crud import create_user_file
from models.user import User
from models.uploaded_file import UploadedFile
from storage.celery_db import SessionLocal  # <-- sync DB for Celery
# from storage.redis_client import  set_temp_data
from storage.redis_sync_client import set_task_progress_sync, set_temp_data_sync
from settings.pydantic_config import settings
from uuid import uuid4
from typing import Optional
import os
from datetime import datetime
import requests

# Configure Cloudinary (sync)
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)


@celery_app.task(bind=True, name="process_small_file", max_retries=3, default_retry_delay=10, time_limit=600, soft_time_limit=540)
def process_small_file(self, form: dict, file: Optional[bytes] = None):
    task_id = self.request.id

    try:
        # Create temp record
        temp_record = {
            "id": task_id,
            "user_id": form["user_id"],
            "name": form.get("file_name", "pending"),
            "extension": "unknown",
            "size": "0 KB",
            "url": "pending",
            "status": "PROCESSING",
            "public_id": "pending",
        }
        set_temp_data_sync(task_id, temp_record)
        set_task_progress_sync(task_id, 10, "STARTED")

        # DB session
        with SessionLocal() as session:
            # Validate user
            user = session.get(User, form["user_id"])
            if not user:
                set_task_progress_sync(task_id, 100, "FAILED")
                raise EntityNotFoundError("Invalid user")

            # Get file content
            if form["source_type"] == "url":
                file_content, file_name, file_extension = download_file_sync(
                    form["file_url"], task_id)
            else:
                if file is None:
                    set_task_progress_sync(task_id, 100, "FAILED")
                    raise ValueError(
                        "File content is required for upload source type")
                file_content = file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                file_extension = detect_file_extension(file_content)
                file_name = form.get('file_name', f"uploaded_file_{timestamp}")

            # Validate file
            if file_extension not in ["csv", "xls", "xlsx"]:
                set_task_progress_sync(task_id, 100, "FAILED")
                raise ValueError(f"Unsupported file type: {file_extension}")

            if len(file_content) > 100 * 1024 * 1024:
                set_task_progress_sync(task_id, 100, "FAILED")
                raise ValueError("File size exceeds 100 MB")

            # Clean if requested
            if form.get("clean_file"):
                set_task_progress_sync(task_id, 60, "CLEANING_DATA")
                file_content = clean_file_with_pandas(
                    file_content, file_extension)
                set_task_progress_sync(task_id, 70, "DATA_CLEANED")

            # Upload to Cloudinary
            set_task_progress_sync(
                task_id, 80, "UPLOADING_TO_EXTERNAL_STORAGE")
            final_filename = f"{file_name}.{file_extension}"
            upload_response = cloudinary.uploader.upload(
                BytesIO(file_content),
                folder="AgeData",
                resource_type="auto",
                public_id=str(uuid4()),
                overwrite=True,
            )

            # Create DB record
            upload_file_details = {
                "id": task_id,
                "name": file_name,
                "extension": file_extension,
                "size": f"{upload_response['bytes'] / 1024:.2f} KB",
                "url": upload_response["secure_url"],
                "user_id": form["user_id"],
                "status": "SUCCESS",
                "public_id": upload_response["public_id"],
            }

            new_file = create_user_file(upload_file_details)
            session.add(new_file)
            session.commit()
            set_task_progress_sync(task_id, 90, "SAVING_TO_DATABASE")

        # Update temp record
        temp_record.update({
            "name": file_name,
            "extension": file_extension,
            "size": f"{upload_response['bytes'] / 1024:.2f} KB",
            "url": upload_response["secure_url"],
            "status": "SUCCESS",
            "public_id": upload_response["public_id"],
        })
        set_temp_data_sync(task_id, temp_record)
        set_task_progress_sync(task_id, 100, "COMPLETED")

        return {
            "task_id": task_id,
            "url": upload_response["secure_url"],
            "file_name": final_filename,
            "user_id": form["user_id"],
            "status": "SUCCESS",
            "public_id": upload_response["public_id"],
        }

    except Exception as exc:
        try:
            set_task_progress_sync(task_id, 100, "FAILED")
        except Exception:
            print(f"Failed to update task progress for {task_id}")
        raise self.retry(exc=exc)


# ----------------- Helper Functions -----------------


def download_file_sync(url: str, task_id: str):
    """Sync file download with progress updates"""
    resp = requests.get(url, stream=True)
    if resp.status_code != 200:
        set_task_progress_sync(task_id, 100, "FAILED",
                               f"Failed to fetch file: HTTP {resp.status_code}")
        raise ValueError(f"Failed to fetch file from {url}")

    total_size = int(resp.headers.get("content-length", 0))
    downloaded_size = 0
    chunks = []
    last_update_percent = 0

    set_task_progress_sync(
        task_id, 30, "DOWNLOADING_FILE", "Starting download...")

    for chunk in resp.iter_content(chunk_size=8192):
        chunks.append(chunk)
        downloaded_size += len(chunk)
        if total_size > 0:
            current_percent = min((downloaded_size / total_size) * 100, 100)
            if current_percent - last_update_percent >= 10:
                global_progress = 30 + (20 * (current_percent / 100))
                global_progress = min(50, global_progress)
                set_task_progress_sync(task_id, int(
                    global_progress), "DOWNLOADING_FILE", f"Downloaded {current_percent:.0f}%")
                last_update_percent = current_percent

    set_task_progress_sync(task_id, 50, "DOWNLOAD_COMPLETE",
                           "Download finished successfully")
    file_content = b''.join(chunks)

    # Determine file name and extension
    filename_from_url = url.split("/")[-1]
    if "." in filename_from_url:
        file_name = filename_from_url.split(".")[0]
        file_extension = filename_from_url.split(".")[-1].lower()
    else:
        file_name = f"downloaded_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        file_extension = detect_file_extension(file_content)

    return file_content, file_name, file_extension


def detect_file_extension(file_content: bytes) -> str:
    """Detect file extension from content (sync)"""
    try:
        if file_content.startswith(b'PK'):
            if b'xl/' in file_content or b'[Content_Types].xml' in file_content:
                return 'xlsx'
            return 'zip'

        try:
            sample = file_content[:1000].decode('utf-8')
            if ',' in sample and '\n' in sample:
                return 'csv'
        except Exception:
            pass

        if file_content.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
            return 'xls'

        return 'csv'
    except Exception:
        return 'csv'
