import cloudinary
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError
from models.uploaded_file import UploadedFile
from storage import db
from schemas.default_response import DefaultResponse
from utils.extract_cloudinary_public_id import extract_cloudinary_public_id_and_type
from settings.pydantic_config import settings


def create_user_file(data: dict):
    """Create a new user file"""
    user_file = UploadedFile(**data)
    return user_file


async def get_user_file_by_id(file_id: str, session: AsyncSession) -> DefaultResponse:
    """Get user file by id"""
    file = await db.get(session, UploadedFile, file_id)
    if not file:
        raise EntityNotFoundError("File not found")
        # Ensure the file is an instance of UploadedFile
    if not isinstance(file, UploadedFile):
        raise EntityNotFoundError("Must provide a valid file ID")
    return DefaultResponse(
        status="success",
        message="File found",
        data=file.to_dict()
    )


async def update_user_file(file_id: str, data: dict, session: AsyncSession) -> DefaultResponse:
    """Update user file by id"""
    file = await db.get(session, UploadedFile, file_id)
    if not file:
        raise EntityNotFoundError("File not found")
        # Ensure the file is an instance of UploadedFile
    if not isinstance(file, UploadedFile):
        raise EntityNotFoundError("Must provide a valid file ID")
    if not data:
        raise DataRequiredError("No data provided")
    await file.update(session, data)
    return DefaultResponse(
        status="success",
        message="File updated",
        data=file.to_dict()
    )


async def delete_user_file(file_id: str, session: AsyncSession) -> DefaultResponse:
    """Delete user file by id (handles Cloudinary-hosted and locally stored files)"""
    import os
    import logging
    log = logging.getLogger(__name__)

    file = await db.get(session, UploadedFile, file_id)
    if not file:
        raise EntityNotFoundError("File not found")
    if not isinstance(file, UploadedFile):
        raise EntityNotFoundError("Must provide a valid file ID")

    is_cloudinary = bool(file.url and file.url.startswith("http") and "cloudinary" in file.url)

    if is_cloudinary:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        public_id = file.public_id
        if not public_id:
            public_id, _ = extract_cloudinary_public_id_and_type(file.url)
        try:
            cloudinary_response = cloudinary.api.delete_resources(
                public_ids=[public_id], resource_type="raw", type="upload"
            )
            deleted_status = cloudinary_response.get("deleted", {}).get(public_id)
            if deleted_status not in ("deleted", "not_found"):
                raise Exception(f"Unexpected Cloudinary response: {cloudinary_response}")
            log.info("Cloudinary delete for %s: %s", public_id, deleted_status)
        except Exception as e:
            raise Exception("Failed to delete file from Cloudinary - error: " + str(e))
    else:
        # Locally stored file — resolve path and remove from disk
        if file.url and not file.url.startswith("http"):
            _here = os.path.dirname(os.path.abspath(__file__))
            backend_root = os.path.normpath(os.path.join(_here, '..', '..', '..', '..'))
            local_path = os.path.normpath(os.path.join(backend_root, file.url.lstrip('/')))
            if os.path.isfile(local_path):
                try:
                    os.remove(local_path)
                    log.info("Deleted local file: %s", local_path)
                except Exception as e:
                    log.warning("Could not delete local file %s: %s", local_path, e)
            else:
                log.warning("Local file not found on disk, skipping fs delete: %s", local_path)

    await file.delete(session)
    return DefaultResponse(
        status="success",
        message="File deleted",
        data={"file_id": file_id}
    )
