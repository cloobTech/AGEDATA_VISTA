## Endpoint

`GET /api/v1/upload-progress/{task_id}`

## Description

This endpoint streams the progress of a file upload task via **Server-Sent Events (SSE)**. The `task_id` is the unique identifier returned after uploading a file. The client can use this endpoint to monitor the progress of the file processing in real-time.

## Request

### URL Parameters

| Name      | Type   | Required | Description                     |
| --------- | ------ | -------- | ------------------------------- |
| `task_id` | string | Yes      | The unique ID of the file upload task. |

### Headers

| Name            | Type   | Required | Description                     |
| --------------- | ------ | -------- | ------------------------------- |
| `Accept`        | string | Yes      | Must be `text/event-stream`.    |

## Response

### Success Response

The response is streamed as **Server-Sent Events (SSE)** with the following fields:

#### Event Data Format
```json
{
    "task_id": "string",
    "progress": "integer (0-100)",
    "status": "string (e.g., STARTED, COMPLETED, FAILED, etc.)",
    "message": "string",
    "file_type": "string",
    "data": {
        "id": "string",
        "name": "string",
        "size": "string",
        "extension": "string",
        "url": "string",
        "user_id": "string",
        "status": "PROCESSING or COMPLETED"
    }
}
```

#### Example Event Data
```json
{
    "task_id": "70f422e1-c593-4062-a7f4-e9a33ac927a3",
    "progress": 80,
    "status": "UPLOADING_TO_EXTERNAL_STORAGE",
    "message": "",
    "file_type": "unknown",
    "data": {
        "id": "70f422e1-c593-4062-a7f4-e9a33ac927a3",
        "name": "deem.png",
        "size": "0 KB",
        "extension": "unknown",
        "url": "pending",
        "user_id": "9c6ab8a3-543e-41a5-a93d-1c23456aeba4",
        "status": "PROCESSING"
    }
}
```

### Streamed Statuses

The following statuses may be streamed during the task's lifecycle:

| Status                          | Description                                      |
|---------------------------------|--------------------------------------------------|
| `STARTED`                       | The task has started.                           |
| `DOWNLOADING_FILE`              | The file is being downloaded.                   |
| `CLEANING_DATA`                 | The file is being cleaned.                      |
| `UPLOADING_TO_EXTERNAL_STORAGE` | The file is being uploaded to external storage. |
| `SAVING_TO_DATABASE`            | The file metadata is being saved to the database. |
| `COMPLETED`                     | The task has been successfully completed.       |
| `FAILED`                        | The task has failed.                            |

### Database Statuses

The `status` field in the `data` object can have the following values:
- `PROCESSING`: The task is still in progress.
- `COMPLETED`: The task has been successfully completed.

### Error Response

- **Status Code:** `500 Internal Server Error`
  - **Detail:** An unexpected error occurred while streaming the task progress.
  - **Example:**
    ```json
    {
      "detail": "An unexpected error occurred."
    }
    ```

## Example Request

```sh
curl -X GET "http://localhost:8000/api/v1/upload-progress/70f422e1-c593-4062-a7f4-e9a33ac927a3" \
-H "Accept: text/event-stream"
```

## Example Success Response (Streamed Event)

```json
data: {
    "task_id": "70f422e1-c593-4062-a7f4-e9a33ac927a3",
    "progress": 80,
    "status": "UPLOADING_TO_EXTERNAL_STORAGE",
    "message": "",
    "file_type": "unknown",
    "data": {
        "id": "70f422e1-c593-4062-a7f4-e9a33ac927a3",
        "name": "deem.png",
        "size": "0 KB",
        "extension": "unknown",
        "url": "pending",
        "user_id": "9c6ab8a3-543e-41a5-a93d-1c23456aeba4",
        "status": "PROCESSING"
    }
}
```

## Example Error Response

```json
{
    "detail": "An unexpected error occurred."
}
```