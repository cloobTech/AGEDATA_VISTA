## Endpoint

`POST /api/v1/file-upload/`

## Description

This endpoint handles file uploads for a specific user. The file can be uploaded directly or fetched from a URL.

## Request

The request should be made with `Content-Type: multipart/form-data` and include the following parameters:

### Form Data Parameters

| Name         | Type      | Required | Description                                      |
| ------------ | --------- | -------- | ------------------------------------------------ |
| `user_id`    | string    | Yes      | The ID of the user.                              |
| `file`       | UploadFile | No      | The file to be uploaded (required if `source_type` is `upload`). |
| `file_type`  | string    | No       | The type of the file (default: `tabular`) or `image`.       |
| `clean_file` | boolean   | No       | Whether to clean the file automatically (default: `false`). |
| `source_type`| string    | Yes      | The source of the file (`upload` or `url`) - (default: `upload`).      |
| `file_url`   | string    | No       | The URL of the file (required if `source_type` is `url`). |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the following keys:

```json
{
    "status": "success",
    "message": "File uploaded successfully",
    "data": {
        "id": "string",
        "name": "string",
        "size": "string",
        "extension": "string (csv, xls ...)", 
        "url": "string"
    }
}
```

### Error Response

- **Status Code:** `400 Bad Request`
  - **Detail:** Missing or invalid parameters.
  - **Example:**
    ```json
    {
      "detail": "Invalid source_type. Must be 'upload' or 'url'."
    }
    ```

- **Status Code:** `500 Internal Server Error`
  - **Detail:** Unexpected error during file processing.
  - **Example:**
    ```json
    {
      "detail": "An unexpected error occurred."
    }
    ```

## Example Request

### Uploading a File
```sh
curl -X POST "http://localhost:8000/api/v1/file-upload/" \
-H "Content-Type: multipart/form-data" \
-F "user_id=12345" \
-F "file=@example.csv" \
-F "file_type=tabular" \
-F "clean_file=true" \
-F "source_type=upload"
```

### Uploading from a URL
```sh
curl -X POST "http://localhost:8000/api/v1/file-upload/" \
-H "Content-Type: multipart/form-data" \
-F "user_id=12345" \
-F "file_type=tabular" \
-F "clean_file=false" \
-F "source_type=url" \
-F "file_url=https://example.com/dataset.csv"
```

## Example Success Response

```json
{
    "status": "success",
    "message": "File uploaded successfully",
    "data": {
        "id": "abc123",
        "name": "example",
        "size": "12.5 KB",
        "extension": "csv",
        "url": "https://res.cloudinary.com/example/dataset.csv"
    }
}
```

## Example Error Response

```json
{
    "detail": "Invalid source_type. Must be 'upload' or 'url'."
}
```