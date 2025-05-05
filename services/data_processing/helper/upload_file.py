import cloudinary.uploader
from sqlalchemy.ext.asyncio import AsyncSession

from io import BytesIO
from errors.exceptions import EntityNotFoundError
from services.data_processing.helper.clean_file import clean_file_with_pandas
from services.data_processing.user_files.crud import create_user_file
from models.user import User
from storage import db


async def process_small_file(file: BytesIO, user_id: str, session: AsyncSession) -> str:
    # async def process_small_file(file: BytesIO) -> str:
    """Upload small files (< 10 MB) to Cloudinary"""
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("Must provide a valid user ID")

    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["csv", "xls", "xlsx"]:
        raise ValueError(
            f"Unsupported file type: {file_extension}. Use 'csv' or 'xlsx'.")

    # Check file size
    file_content = await file.read()
    if len(file_content) > 100 * 1024 * 1024:  # 100 MB
        raise ValueError("File size exceeds the 100 MB limit.")

    # Clean up the file
    cleaned_file = clean_file_with_pandas(file_content, file_extension)

    response = cloudinary.uploader.upload(
        BytesIO(cleaned_file), folder="AgeData", resource_type="auto", overwrite=True)
    # create a file object and attach it to a user

    upload_file_details = {
        "name": file.filename.split(".")[0],
        "extension": file_extension,
        "size": f"{response['bytes'] / 1024:.2f} KB",
        "url": response["secure_url"],
        "user_id": user_id

    }

    new_file = create_user_file(upload_file_details)
    # user.awaitable_attrs.files.append(new_file)
    # await user.save(session)
    await new_file.save(session)
    return new_file.to_dict()
