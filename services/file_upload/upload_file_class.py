# services/file_upload/upload_file_class.py
from fastapi import UploadFile, HTTPException
from celery_app import celery_app
from services.data_processing.helper.upload_file import process_small_file
from typing import Optional
import os
import uuid
import logging

logger = logging.getLogger(__name__)

# Uploads directory for local fallback storage
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "uploads", "datasets")
os.makedirs(UPLOADS_DIR, exist_ok=True)


def _is_celery_available() -> bool:
    """Check if Celery broker (Redis) is reachable."""
    try:
        celery_app.connection_for_write().ensure_connection(max_retries=1, timeout=2)
        return True
    except Exception:
        return False


class FileUploadService:
    def __init__(self):
        self.allowed_extensions = ['csv', 'xls', 'xlsx']
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.allowed_file_types = ['tabular', 'image']  # Add more as needed

    async def validate_upload_file(self, file: UploadFile):
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        file_extension = file.filename.split('.')[-1].lower()

        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {', '.join(self.allowed_extensions)}"
            )

        return file_extension

    async def validate_file_size(self, file_content: bytes):
        """Validate file size"""
        if len(file_content) > self.max_file_size:
            raise HTTPException(status_code=400, detail="File size exceeds 100MB limit")

    async def validate_form_data(self, form_data: dict, file: Optional[UploadFile]):
        """Validate form data including file_type and source_type"""
        file_type = form_data.get("file_type", "tabular")

        if file_type not in self.allowed_file_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{file_type}' not supported. Allowed: {', '.join(self.allowed_file_types)}"
            )

        # Validate source_type and file_url
        source_type = form_data.get("source_type")
        if source_type == "url" and not form_data.get("file_url"):
            raise HTTPException(
                status_code=400,
                detail="file_url is required when source_type is 'url'"
            )

        # FIXED: Check the file parameter directly, not in form_data
        if source_type == "upload" and not file:
            raise HTTPException(
                status_code=400,
                detail="File is required when source_type is 'upload'"
            )

    async def prepare_upload_data(
        self,
        file: Optional[UploadFile],
        form: dict
    ):
        """Prepare data for file upload processing"""
        # Validate form data first - pass the file parameter
        await self.validate_form_data(form, file)

        file_content = None
        if form["source_type"] == "upload":
            # We already validated that file exists above
            file_extension = await self.validate_upload_file(file)
            file_content = await file.read()
            await self.validate_file_size(file_content)

        # Prepare form data for Celery task
        form_data = {
            "user_id": form["user_id"],
            "file_type": form["file_type"],
            "clean_file": form["clean_file"],
            "source_type": form["source_type"],
            "file_url": form.get("file_url"),
            "file_name": file.filename if file else None
        }

        return form_data, file_content

    async def _process_file_locally(self, form_data: dict, file_content: Optional[bytes]) -> dict:
        """
        Process file upload directly (synchronous local storage fallback).
        Used when Celery/Redis is not available.
        Saves the file to the local uploads/ directory and inserts a DB record.
        """
        import asyncio
        from datetime import datetime
        from services.data_processing.helper.upload_file import detect_file_extension
        from services.data_processing.user_files.crud import create_user_file
        from storage import db
        from storage.database import DBStorage
        from settings.pydantic_config import settings

        file_id = str(uuid.uuid4())
        file_content_bytes = file_content or b""
        file_name_raw = form_data.get("file_name") or f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        # Strip extension from filename if present
        if "." in file_name_raw:
            base_name = file_name_raw.rsplit(".", 1)[0]
            file_extension = file_name_raw.rsplit(".", 1)[1].lower()
        else:
            base_name = file_name_raw
            file_extension = detect_file_extension(file_content_bytes)

        final_filename = f"{base_name}.{file_extension}"
        local_path = os.path.join(UPLOADS_DIR, f"{file_id}_{final_filename}")

        # Save file to disk
        with open(local_path, "wb") as f:
            f.write(file_content_bytes)

        size_kb = f"{len(file_content_bytes) / 1024:.2f} KB"
        local_url = f"/uploads/datasets/{file_id}_{final_filename}"

        file_details = {
            "id": file_id,
            "name": base_name,
            "extension": file_extension,
            "size": size_kb,
            "url": local_url,
            "user_id": form_data["user_id"],
            "status": "SUCCESS",
            "public_id": file_id,
        }

        # Write to DB using the app's async session
        async with db.get_session() as session:
            new_file = create_user_file(file_details)
            session.add(new_file)
            await session.commit()
            await session.refresh(new_file)
            result_dict = new_file.to_dict()

        logger.info("Local fallback upload saved: %s -> %s", final_filename, local_path)
        return result_dict

    async def start_file_processing(self, form_data: dict, file_content: Optional[bytes]):
        """
        Start file processing.
        Attempts Celery first; falls back to synchronous local processing if Redis is unavailable.
        """
        if _is_celery_available():
            task = process_small_file.delay(form_data, file_content)
            return {
                "id": task.id,
                "status": "processing",
                "progress_url": f"/api/v1/file-upload/upload-progress/{task.id}",
                "message": f"{form_data['file_type'].title()} file processing started",
                "file_type": form_data["file_type"],
                "source_type": form_data["source_type"]
            }
        else:
            logger.warning("Celery/Redis unavailable — using local synchronous upload fallback")
            result = await self._process_file_locally(form_data, file_content)
            return result


file_upload_service = FileUploadService()