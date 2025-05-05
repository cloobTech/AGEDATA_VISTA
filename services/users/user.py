import cloudinary.api
from fastapi import UploadFile
from io import BytesIO
import cloudinary.uploader
from sqlalchemy.ext.asyncio import AsyncSession
from errors.exceptions import EntityNotFoundError,  DataRequiredError
from storage import db
from schemas.default_response import DefaultResponse
from models.user import User
from utils.extract_cloudinary_public_id import extract_public_id


async def get_all_users(session: AsyncSession):
    users = await db.all(session, User)
    if not users:
        return DefaultResponse(
            status="success",
            message="No users found",
            data=[]
        )
    user_data = [user.to_dict() for user in users.values()]
    return DefaultResponse(
        status="success",
        message="Users found",
        data=user_data
    )


async def get_user_by_id(user_id: str, params: str, session: AsyncSession):
    param_list = [param.strip()
                  for param in params.split(",")] if params else None
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")
    if param_list:
        for relationship in param_list:
            try:
                await getattr(user.awaitable_attrs, relationship)
            except AttributeError:
                pass
    return DefaultResponse(
        status="success",
        message="User found",
        data=user.to_dict(include=param_list)
    )


async def update_user(user_id: str, user_data: dict, session: AsyncSession):
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")
    if not user_data:
        raise DataRequiredError("Must provide data to update")
    await user.update(session, user_data)
    await user.save(session)
    return DefaultResponse(
        status="success",
        message="User updated",
        data=user.to_dict()
    )


async def upload_user_picture(file: UploadFile, user_id: str, session: AsyncSession):
    """Upload a picture to Cloudinary and associate it with a user."""
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("Must provide a valid user ID")

    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["jpg", "jpeg", "png", "gif"]:
        raise ValueError(
            f"Unsupported file type: {file_extension}. Use 'jpg', 'jpeg', 'png', or 'gif'.")

    # Read and validate file content
    file_content = await file.read()
    if len(file_content) > 10 * 1024 * 1024:  # 10 MB
        raise ValueError("File size exceeds the 10 MB limit.")

    # Delete the existing profile picture from Cloudinary if it exists
    if user.profile_picture:
        try:
            public_id = [extract_public_id(user.profile_picture)]
            cloudinary.api.delete_resources(
                public_id, resource_type="image", type="upload")
        except Exception as e:
            raise ValueError(
                f"Failed to delete existing profile picture: {str(e)}")

    # Upload the new picture to Cloudinary
    response = cloudinary.uploader.upload(
        BytesIO(file_content),
        folder="AgeDataUserPictures",
        resource_type="image",
        overwrite=True
    )

    # Update user profile picture URL and save
    user.profile_picture = response["secure_url"]
    await user.save(session)

    return DefaultResponse(
        status="success",
        message="User picture uploaded successfully",
        data=user.to_dict()
    )


async def delete_user(user_id: str, session: AsyncSession):
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("User not found")
    await db.delete(session, user)
    return DefaultResponse(
        status="success",
        message="User deleted",
        data=user.to_dict()
    )
