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
        # Load the file into a DataFrame
        if file_extension == "csv":
            df = pd.read_csv(BytesIO(file_content))
        elif file_extension in ["xls", "xlsx"]:
            df = pd.read_excel(BytesIO(file_content))
        elif file_extension == "json":
            df = pd.read_json(BytesIO(file_content))
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        # Remove duplicates
        df = df.drop_duplicates()

        # Handle missing values (fill with empty string or remove)
        df = df.fillna("")

        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace(r"[^a-z0-9_]", "", regex=True)

        # Try converting datetime-like columns
        for col in df.columns:
            if "date" in col or "time" in col:
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass  # silently skip if it fails

        # Convert non-datetime columns to string
        for col in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)

        # Drop columns with all missing values
        df = df.dropna(axis=1, how="all")

        # Write cleaned data to BytesIO
        output = BytesIO()
        if file_extension == "csv":
            df.to_csv(output, index=False)
        elif file_extension in ["xls", "xlsx"]:
            df.to_excel(output, index=False, engine="openpyxl")
        elif file_extension == "json":
            df.to_json(output, orient="records")

        return output.getvalue()

    except Exception as e:
        print(f"Error cleaning file: {e}")
        raise ValueError("Error cleaning file") from e
