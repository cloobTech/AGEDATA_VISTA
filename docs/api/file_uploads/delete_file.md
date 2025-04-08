# API Route: `DELETE /api/v1/file-upload/{file_id}`

## Description
Deletes a file by its unique identifier. This route interacts with the database and Cloudinary to remove the file and its reference.

---

## Endpoint

| Method | URL                              | Description              |
|--------|----------------------------------|--------------------------|
| `DELETE` | `/api/v1/file-upload/{file_id}` | Deletes a file by its ID. |

---

## Parameters

| Name       | Type            | Location   | Required | Description                     |
|------------|-----------------|------------|----------|---------------------------------|
| `file_id`  | `str`           | Path       | Yes      | The unique identifier of the file to delete. |

---

## Responses

### Success Response
| Status Code | Description                                      |
|-------------|--------------------------------------------------|
| `200 OK`    | File successfully deleted.                      |

#### Example Response
```json
{
    "status": "success",
    "message": "File deleted",
    "data": {
        "file_id": "12345"
    }
}