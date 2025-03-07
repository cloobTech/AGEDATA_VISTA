import os
import tempfile
from pyspark.sql import SparkSession
from io import BytesIO

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
            raise ValueError(f"Unsupported file type: {file_extension}. Use 'csv' or 'xlsx'.")

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
