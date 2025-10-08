## Endpoint

`GET /api/v1/task-status/{task_id}`

## Description

This endpoint retrieves the current status of a specific task. Unlike the streaming endpoint, this provides a one-time snapshot of the task's progress.

## Request

### URL Parameters

| Name      | Type   | Required | Description                     |
| --------- | ------ | -------- | ------------------------------- |
| `task_id` | string | Yes      | The unique ID of the task.       |

### Headers

| Name            | Type   | Required | Description                     |
| --------------- | ------ | -------- | ------------------------------- |
| `Accept`        | string | Yes      | Must be `application/json`.     |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the current status of the task.

```json
{
    "status": "success",
    "message": "Task status retrieved",
    "data": {
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
}
```

### Task Statuses

The `status` field may include the following values:

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

- **Status Code:** `404 Not Found`
  - **Detail:** Task not found.
  - **Example:**
    ```json
    {
      "detail": "Task not found"
    }
    ```

- **Status Code:** `500 Internal Server Error`
  - **Detail:** An unexpected error occurred while retrieving the task status.
  - **Example:**
    ```json
    {
      "detail": "An unexpected error occurred."
    }
    ```

## Example Request

```sh
curl -X GET "http://localhost:8000/api/v1/task-status/70f422e1-c593-4062-a7f4-e9a33ac927a3" \
-H "Accept: application/json"
```

## Example Success Response

```json
{
    "status": "success",
    "message": "Task status retrieved",
    "data": {
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
}
```

## Example Error Response

```json
{
    "detail": "Task not found"
}
```