import cloudinary
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError
from models.uploaded_file import UploadedFile
from storage import db
from schemas.default_response import DefaultResponse
from utils.extract_cloudinary_public_id import extract_public_id


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
    """Delete user file by id"""
    file = await db.get(session, UploadedFile, file_id)
    if not file:
        raise EntityNotFoundError("File not found")
        # Ensure the file is an instance of UploadedFile
    if not isinstance(file, UploadedFile):
        raise EntityNotFoundError("Must provide a valid file ID")

    public_ids = [extract_public_id(file.url)]

    # Delete the file from Cloudinary
    cloudinary_response = cloudinary.api.delete_resources(
        public_ids, resource_type="raw", type="upload")
    if cloudinary_response.get("deleted")[public_ids[0]] == "not_found":
        raise Exception("Failed to delete file from Cloudinary")

    # # Delete the file object/refrence from the database
    await file.delete(session)
    return DefaultResponse(
        status="success",
        message="File deleted",
        data={
            "file_id": file_id
        }
    )
