import cloudinary.uploader
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
from PIL import Image
from errors.exceptions import EntityNotFoundError
from services.data_processing.user_files.crud import create_user_file
from models.user import User
from storage import db
from schemas.upload_dataset import UploadForm
from fastapi import UploadFile
import asyncio

async def process_image_file(
    file: UploadFile | bytes,  # Accept both UploadFile and bytes
    form: UploadForm,
    session: AsyncSession,
    max_width: int = 1920,
    max_height: int = 1080,
    quality: int = 85
) -> dict:
    """Upload image files to Cloudinary with optional resizing and optimization"""
    # Validate user exists
    user_id = form.user_id
    user = await db.get(session, User, user_id)
    if not user:
        raise EntityNotFoundError("Must provide a valid user ID")

    # Handle both UploadFile and bytes input
    if isinstance(file, bytes):
        # If bytes are provided, we need filename from form or generate one
        file_content = file
        file_extension = form.file_name.split(".")[-1].lower() if form.file_name else "jpg"
        original_filename = form.file_name or f"image_{user_id}.{file_extension}"
    else:
        # Original UploadFile handling
        file_content = await file.read()
        file_extension = file.filename.split(".")[-1].lower()
        original_filename = file.filename

    # Validate file extension
    supported_formats = ["jpg", "jpeg", "png", "webp", "gif"]
    if file_extension not in supported_formats:
        raise ValueError(
            f"Unsupported image format: {file_extension}. Supported formats: {', '.join(supported_formats)}")

    # Validate file size (10MB limit for images)
    if len(file_content) > 10 * 1024 * 1024:
        raise ValueError("Image size exceeds the 10 MB limit.")

    # Optional: Process image with PIL (resize, optimize)
    try:
        img = Image.open(BytesIO(file_content))

        # Resize if needed while maintaining aspect ratio
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height))

            # Save optimized version to buffer
            buffer = BytesIO()
            if file_extension in ["jpg", "jpeg"]:
                img.save(buffer, format="JPEG", quality=quality, optimize=True)
            elif file_extension == "png":
                img.save(buffer, format="PNG", optimize=True)
            elif file_extension == "webp":
                img.save(buffer, format="WEBP", quality=quality)
            else:
                # For formats we don't process (like GIF), use original
                buffer = BytesIO(file_content)

            file_content = buffer.getvalue()
    except Exception as e:
        # If image processing fails, proceed with original
        print(f"Image processing error, using original: {str(e)}")

    # Upload to Cloudinary
    response = cloudinary.uploader.upload(
        BytesIO(file_content),
        folder="user_images",
        resource_type="image",
        quality=quality,
        format=file_extension if file_extension != 'jpg' else 'jpeg'  # Cloudinary uses 'jpeg'
    )

    # Create file record in database
    upload_file_details = {
        "name": original_filename.split(".")[0],
        "extension": file_extension,
        "size": f"{response['bytes'] / 1024:.2f} KB",
        "url": response["secure_url"],
        "user_id": form.user_id
    }

    new_file = create_user_file(upload_file_details)
    await new_file.save(session)

    return new_file.to_dict()