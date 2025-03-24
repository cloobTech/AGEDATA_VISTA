import os
import aiohttp
import tempfile
from pyspark.sql import SparkSession
from io import BytesIO
from utils.async_request import fetch_cloudinary_file
from errors.exceptions import EntityNotFoundError
from sqlalchemy.ext.asyncio import AsyncSession
from storage import db
from models.uploaded_file import UploadedFile
from typing import Dict, Any
import requests


# from services.data_processing.helper.clean_file import clean_file_with_pyspark


import pandas as pd
from io import BytesIO
from fastapi import HTTPException

import pandas as pd
from io import BytesIO
from fastapi import HTTPException


async def load_data_with_pandas(file_id: str, session: AsyncSession) -> pd.DataFrame:
    """Fetch Data from the user file and load it into a pandas DataFrame."""
    # Fetch the file metadata from the database
    file = await db.get(session, UploadedFile, file_id)
    if not file:
        raise EntityNotFoundError("Must provide a valid file ID")
    file_type = file.extension.lower()

    file_content = await fetch_cloudinary_file(file.url)

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
    return df


def load_data(spark: SparkSession, file: BytesIO, filename: str):
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
