## Endpoint

`POST /api/v1/file-upload/`

## Description

This endpoint allows users to upload files for processing. Files can be uploaded directly or fetched from a URL.

## Request

The request should be made with `Content-Type: multipart/form-data` and include the following parameters:

### Form Data Parameters

| Name          | Type       | Required | Description                                                      |
| ------------- | ---------- | -------- | ---------------------------------------------------------------- |
| `user_id`     | string     | Yes      | The ID of the user.                                              |
| `file`        | UploadFile | No       | The file to be uploaded (required if `source_type` is `upload`). |
| `file_type`   | string     | No       | The type of the file (default: `tabular`).                       |
| `clean_file`  | boolean    | No       | Whether to clean the file before processing (default: `false`).  |
| `source_type` | string     | Yes      | The source of the file (`upload` or `url`).                      |
| `file_url`    | string     | No       | The URL of the file (required if `source_type` is `url`).        |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the following:

```json
{
  "status": "success",
  "message": "File submitted for processing",
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
  "message": "File submitted for processing",
  "data": {
    "id": "501d478a-1694-41ed-8201-4c3e671e7ca7",
    "status": "processing",
    "progress_url": "/api/v1/file-upload/upload-progress/501d478a-1694-41ed-8201-4c3e671e7ca7",
    "message": "Tabular file processing started",
    "file_type": "tabular",
    "source_type": "url"
  }
}
```

## Example Error Response

```json
{
  "detail": "Invalid source_type. Must be 'upload' or 'url'."
}
```
