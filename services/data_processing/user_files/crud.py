from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError, DataRequiredError
from models.user import User
from models.uploaded_file import UploadedFile
from storage import db


def create_user_file(data: dict):
    """Create a new user file"""
    user_file = UploadedFile(**data)
    return user_file