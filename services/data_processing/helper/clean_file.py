import pandas as pd
from io import BytesIO


def clean_file_with_pandas(file_content: bytes, file_extension: str) -> bytes:
    """
    Clean a small file (CSV, Excel, or JSON) using Pandas and return the cleaned data as bytes.

    :param file_content: File content as bytes.
    :param file_extension: File extension (e.g., "csv", "xlsx", "json").
    :return: Cleaned file content as bytes.
    """
    try:
        # Load the file content into a Pandas DataFrame
        if file_extension == "csv":
            df = pd.read_csv(BytesIO(file_content))
        elif file_extension in ["xls", "xlsx"]:
            df = pd.read_excel(BytesIO(file_content))
        elif file_extension == "json":
            df = pd.read_json(BytesIO(file_content))
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        # Perform generic cleaning
        # 1. Remove duplicates
        df = df.drop_duplicates()

        # 2. Handle missing values (fill with empty string or remove rows)
        # Or use df.dropna() to remove rows with missing values
        df = df.fillna("")

        # 3. Standardize column names
        df.columns = df.columns.str.lower().str.replace(
            " ", "_").str.replace("[^a-z0-9_]", "")

        # 4. Convert data types (example: convert all columns to string)
        df = df.astype(str)

        # 5. Remove unnecessary columns (example: remove columns with all missing values)
        df = df.dropna(axis=1, how="all")

        # Save the cleaned data to a BytesIO object
        output = BytesIO()
        if file_extension == "csv":
            df.to_csv(output, index=False)
        elif file_extension in ["xls", "xlsx"]:
            df.to_excel(output, index=False, engine="openpyxl")
        elif file_extension == "json":
            df.to_json(output, orient="records")

        # Return the cleaned data as bytes
        return output.getvalue()
    except Exception as e:
        print(f"Error cleaning file: {e}")
        raise ValueError("Error cleaning file") from e
