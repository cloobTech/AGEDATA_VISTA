# import asyncio
# from fastapi import UploadFile
# from io import BytesIO
# from services.data_processing.helper.upload_file import process_small_file


# async def test_process_small_file():
#     # Create a sample CSV file content
#     csv_content = b"feature1,feature2,feature3,target\n1.0,2.0,3.0,10.0\n2.0,3.0,4.0,15.0\n"
#     file = UploadFile(filename="sample.csv", file=BytesIO(csv_content))

#     # Call the process_small_file function
#     try:
#         url = await process_small_file(file)
    
#         print(f"File uploaded successfully: {url}")
#     except ValueError as e:
#         print(f"ValueError: {e}")
#     except Exception as e:
#         print(f"Exception: {e}")


# # Run the test
# asyncio.run(test_process_small_file())


# import requests
# import pandas as pd
# from io import BytesIO

# def download_file_from_cloudinary(url: str, file_extension: str) -> pd.DataFrame:
#     print("STARTING DOWNLOAD...")
#     response = requests.get(url)
#     print("DOWNLOAD SUCCESSFUL")
#     response.raise_for_status()  # Check if the request was successful
#     print("DOWNLOAD SUCCESSFUL")

#     file_content = BytesIO(response.content)

#     # Read the file content using pandas
#     if file_extension == "csv":
#         df = pd.read_csv(file_content)
#     elif file_extension in ["xls", "xlsx"]:
#         df = pd.read_excel(file_content)
#     else:
#         raise ValueError(f"Unsupported file type: {file_extension}")

#     return df

# # Example usage
# url = "https://res.cloudinary.com/ddheqirld/raw/upload/v1741446672/AgeData/eiulmwprursy2eewvzso"
# file_extension = "csv"  # Replace with the actual file extension
# df = download_file_from_cloudinary(url, file_extension)
# print(df)

"""
DEV_ENV=dev
SECRET_KEY=super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=520
REFRESH_TOKEN_EXPIRE_DAYS=30
EMAIL_CONFIG_USERNAME=belkid98@gmail.com
EMAIL_CONFIG_PASSWORD=jdlcelwnuzcpfoil
DATABASE_URL=sqlite+aiosqlite:///db.sqlite3
CLOUDINARY_CLOUD_NAME=ddheqirld
CLOUDINARY_API_KEY=933716352435599
CLOUDINARY_API_SECRET=5M6gHwz0lRJqw0HPfFpVY_EGKU4
GOOGLE_CLIENT_ID=448662846551-qvhe4c4l0v1uremqkkbpj3235lddq69r.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
FRONTEND_URL=http://localhost:3000
"""