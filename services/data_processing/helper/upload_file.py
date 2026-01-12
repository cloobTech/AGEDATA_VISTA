import cloudinary
from celery_app import celery_app
import cloudinary.uploader
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from io import BytesIO
from errors.exceptions import EntityNotFoundError
from services.data_processing.helper.clean_file import clean_file_with_pandas
from services.data_processing.user_files.crud import create_user_file
from schemas.upload_dataset import UploadForm
from models.user import User
from models.uploaded_file import UploadedFile
from storage import db
from storage.redis_client import set_task_progress, set_temp_data
from settings.pydantic_config import settings
from uuid import uuid4
from typing import Optional
import asyncio
import os
from datetime import datetime


# Create a global event loop or use the current one
def get_or_create_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


@celery_app.task(bind=True, name="process_small_file", max_retries=3, default_retry_delay=10)
def process_small_file(self, form: dict, file: Optional[bytes] = None):
    task_id = self.request.id
    loop = get_or_create_event_loop()

    try:
        result = loop.run_until_complete(
            process_file_with_progress(task_id, form, file))
        return result
    except Exception as exc:
        # Use the existing loop for error handling to avoid event loop conflicts
        try:
            loop.run_until_complete(set_task_progress(task_id, 100, "FAILED"))
        except Exception:
            # If we can't update progress, just log and continue
            print(f"Failed to update task progress for {task_id}")
        raise self.retry(exc=exc)


async def process_file_with_progress(task_id: str, form: dict, file: Optional[bytes] = None):
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )

    async with db.get_session() as session:
        # Create temp record
        temp_record = {
            "id": task_id,
            "user_id": form["user_id"],
            "name": form['file_name'] if 'file_name' in form else "pending",
            "extension": "unknown",
            "size": "0 KB",
            "url": "pending",
            "status": "PROCESSING",
            "public_id": "pending",
        }

        await set_temp_data(task_id, temp_record, expire=3600)
        await set_task_progress(task_id, 10, "STARTED")

        # Validate user
        user = await session.get(User, form["user_id"])
        if not user:
            await set_task_progress(task_id, 100, "FAILED")
            raise EntityNotFoundError("Invalid user")

        # Download or read file
        file_content: bytes
        file_name: str
        file_extension: str

        if form["source_type"] == "url":
            file_content = await download_file_with_progress(form["file_url"], task_id)
            filename_from_url = form["file_url"].split("/")[-1]

            # Extract name and extension from URL
            if "." in filename_from_url:
                file_name = filename_from_url.split(".")[0]
                file_extension = filename_from_url.split(".")[-1].lower()
            else:
                # If no extension in URL, generate a name and try to detect extension
                file_name = f"downloaded_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                file_extension = await detect_file_extension(file_content)

        else:
            # For uploaded files without filename
            if file is None:
                await set_task_progress(task_id, 100, "FAILED")
                raise ValueError(
                    "File content is required for upload source type")

            file_content = file

            # Generate filename and detect extension
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_extension = await detect_file_extension(file_content)
            file_name = form[
                'file_name'] if 'file_name' in form else f"uploaded_file_{timestamp}"

        # Validate file extension
        if file_extension not in ["csv", "xls", "xlsx"]:
            await set_task_progress(task_id, 100, "FAILED")
            raise ValueError(
                f"Unsupported file type: {file_extension}. Use 'csv', 'xls', or 'xlsx'.")

        # Check file size
        if len(file_content) > 100 * 1024 * 1024:  # 100 MB
            await set_task_progress(task_id, 100, "FAILED")
            raise ValueError("File size exceeds the 100 MB limit.")

        # Clean if requested
        if form.get("clean_file"):
            file_content = await clean_file_with_progress(file_content, file_extension, task_id)

        # Upload to Cloudinary (thread-safe)
        await set_task_progress(task_id, 80, "UPLOADING_TO_EXTERNAL_STORAGE")

        # Generate final filename with extension
        final_filename = f"{file_name}.{file_extension}"

        loop = asyncio.get_running_loop()
        upload_response = await loop.run_in_executor(
            None,
            lambda: cloudinary.uploader.upload(
                BytesIO(file_content),
                folder="AgeData",
                resource_type="auto",
                public_id=str(uuid4()),
                overwrite=True,
            )
        )

        # Create final file record in database
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
        await new_file.save(session)
        await set_task_progress(task_id, 90, "SAVING_TO_DATABASE")

        # Update temp record with final data
        temp_record.update({
            "name": file_name,
            "extension": file_extension,
            "size": f"{upload_response['bytes'] / 1024:.2f} KB",
            "url": upload_response["secure_url"],
            "status": "SUCCESS",
            "public_id": upload_response["public_id"],
        })

        await set_temp_data(task_id, temp_record, expire=3600)
        await set_task_progress(task_id, 100, "COMPLETED")

        return {
            "task_id": task_id,
            "url": upload_response["secure_url"],
            # "file_id": new_file.id,
            "file_name": final_filename,
            "user_id": form["user_id"],
            "status": "SUCCESS",
            "public_id": upload_response["public_id"],
        }


async def detect_file_extension(file_content: bytes) -> str:
    """Detect file extension from content using magic bytes"""
    try:
        # Check for CSV (text file, often starts with text or has comma separation)
        if file_content.startswith(b'PK'):
            # ZIP file (Excel files are ZIP archives)
            if b'xl/' in file_content or b'[Content_Types].xml' in file_content:
                return 'xlsx'
            else:
                return 'zip'

        # Check for CSV (try to decode as text and look for commas)
        try:
            sample = file_content[:1000].decode('utf-8')
            if ',' in sample and '\n' in sample:
                return 'csv'
        except:
            pass

        # Check for XLS (older Excel format)
        if file_content.startswith(b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'):
            return 'xls'

        # Default to CSV if we can't determine
        return 'csv'

    except Exception:
        # Fallback to CSV
        return 'csv'


async def download_file_with_progress(url: str, task_id: str) -> bytes:
    """Download file with progress tracking (30% → 50%)"""
    async with httpx.AsyncClient() as client:
        async with client.stream('GET', url) as response:
            if response.status_code != 200:
                await set_task_progress(
                    task_id, 100, "FAILED", f"Failed to fetch file: HTTP {response.status_code}"
                )
                raise ValueError(f"Failed to fetch the file from: {url}")

            total_size = int(response.headers.get('content-length', 0))
            chunks = []
            downloaded_size = 0
            last_update_percent = 0

            # Start download phase
            await set_task_progress(task_id, 30, "DOWNLOADING_FILE", "Starting download...")

            async for chunk in response.aiter_bytes():
                chunks.append(chunk)
                downloaded_size += len(chunk)

                if total_size > 0:
                    # Calculate current percent (cap at 100)
                    current_percent = min(
                        (downloaded_size / total_size) * 100, 100)

                    # Only update every 10% increment
                    if current_percent - last_update_percent >= 10:
                        # Map 0–100% download to 30–50% overall progress
                        global_progress = 30 + (20 * (current_percent / 100))
                        global_progress = min(50, global_progress)

                        try:
                            await set_task_progress(
                                task_id,
                                int(global_progress),
                                "DOWNLOADING_FILE",
                                f"Downloaded {current_percent:.0f}%"
                            )
                            last_update_percent = current_percent
                        except Exception as e:
                            print(f"Progress update failed: {e}")

                else:
                    # No content-length header → can’t compute percent
                    # Just update linearly every few MB downloaded
                    if downloaded_size // (5 * 1024 * 1024) > last_update_percent:
                        global_progress = min(
                            50, 30 + (downloaded_size / (50 * 1024 * 1024)) * 20)
                        await set_task_progress(
                            task_id,
                            int(global_progress),
                            "DOWNLOADING_FILE",
                            f"Downloaded approx. {downloaded_size / (1024 * 1024):.1f} MB"
                        )
                        last_update_percent = downloaded_size // (
                            5 * 1024 * 1024)

            # Mark download complete
            await set_task_progress(task_id, 50, "DOWNLOAD_COMPLETE", "Download finished successfully")

            return b''.join(chunks)


async def clean_file_with_progress(file_content: bytes, file_extension: str, task_id: str) -> bytes:
    """Clean file with progress updates."""
    try:
        # Update progress for cleaning start
        await set_task_progress(task_id, 60, "CLEANING_DATA")

        # Clean the file
        cleaned_content = clean_file_with_pandas(file_content, file_extension)

        # Update progress after cleaning
        await set_task_progress(task_id, 70, "DATA_CLEANED")

        return cleaned_content
    except Exception as e:
        await set_task_progress(task_id, 100, "FAILED")
        raise e
