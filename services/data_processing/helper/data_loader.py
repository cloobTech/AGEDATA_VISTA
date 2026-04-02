import os
import tempfile
from io import BytesIO
from utils.async_request import fetch_cloudinary_file
from utils.safe_path import safe_local_path
from errors.exceptions import EntityNotFoundError
from sqlalchemy.ext.asyncio import AsyncSession
from storage import db
from models.uploaded_file import UploadedFile
import pandas as pd
from typing import Optional, cast


def _resolve_local_path(url: str) -> Optional[str]:
    """
    If *url* looks like a local path (starts with /uploads/...) resolve it
    safely to an absolute filesystem path. Returns None if it looks like an
    HTTP URL or if the resolved file does not exist.

    Uses safe_local_path() to prevent CWE-22 path traversal.
    """
    if url and url.startswith("/uploads/"):
        try:
            abs_path = safe_local_path(url)
        except ValueError:
            # Traversal attempt — reject silently and fall through to remote
            return None
        if os.path.exists(abs_path):
            return abs_path
    return None


async def _fetch_file_content(url: str) -> bytes:
    """
    Fetch file content from either a local path or a remote URL.
    """
    local = _resolve_local_path(url)
    if local:
        with open(local, "rb") as f:
            return f.read()
    # Fall back to remote fetch (Cloudinary or any HTTP URL)
    return await fetch_cloudinary_file(url)


async def load_data_with_pandas(file_id: str, session: AsyncSession, columns: list = []) -> pd.DataFrame:
    """Fetch Data from the user file and load it into a pandas DataFrame."""
    # Fetch the file metadata from the database
    file = await db.get(session, UploadedFile, file_id)

    # Ensure the file is an instance of UploadedFile
    if not isinstance(file, UploadedFile):
        raise EntityNotFoundError("Must provide a valid file ID")

    file_type = file.extension.lower()
    file_content = await _fetch_file_content(file.url)
    file_obj = BytesIO(file_content)  # Convert bytes to file-like object

    if file_type == "csv":
        df = pd.read_csv(file_obj)
    elif file_type == "json":
        df = pd.read_json(file_obj)
    elif file_type in ["xls", "xlsx"]:
        df = pd.read_excel(file_obj, engine="openpyxl")
    else:
        raise ValueError(
            "Unsupported file type. Use 'csv', 'json', or 'excel'.")

    # If specific columns are provided, select only those columns
    if columns:
        missing_columns = [col for col in columns if col not in df.columns]
        if missing_columns:
            raise ValueError(
                f"The following columns are not in the file: {missing_columns}")
        df = df[columns]

    return df


def load_data(spark, file: BytesIO, filename: str):  # spark: SparkSession (optional dependency)
    """
    Load a CSV or Excel file into a Spark DataFrame.

    :param spark: Spark session
    :param file: File object (BytesIO)
    :param filename: Original filename (to determine file type)
    :return: Spark DataFrame
    """
    file_extension = filename.split(".")[-1].lower()

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        temp_path = temp_file.name
        file.seek(0)  # Reset the file pointer
        temp_file.write(file.read())  # Write content to the temp file

    try:
        if file_extension == "csv":
            df = spark.read.csv(temp_path, header=True, inferSchema=True)
        elif file_extension in ["xls", "xlsx"]:
            df = spark.read.format("com.crealytics.spark.excel") \
                .option("useHeader", "true") \
                .option("inferSchema", "true") \
                .load(temp_path)
        else:
            raise ValueError(
                f"Unsupported file type: {file_extension}. Use 'csv' or 'xlsx'.")

        # Force Spark to read the file immediately before deleting it
        df = df.cache()  # Cache forces Spark to persist data in memory/disk
        df.count()  # Triggers an actual read to load data

        return df

    except Exception as e:
        print(f"Error loading file: {e}")
        return None

    finally:
        # Ensure cleanup of the temporary file after Spark has read it
        if os.path.exists(temp_path):
            os.remove(temp_path)
