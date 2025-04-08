# API Route: `GET /api/v1/file-upload/{file_id}`

## Description
Fetches a file object by its unique identifier. This route retrieves the file details from the database.

---

## Endpoint

| Method | URL                              | Description              |
|--------|----------------------------------|--------------------------|
| `GET`  | `/api/v1/file-upload/{file_id}`  | Retrieves a file by its ID. |

---

## Parameters

### Path Parameters
| Name       | Type   | Required | Description                     |
|------------|--------|----------|---------------------------------|
| `file_id`  | `str`  | Yes      | The unique identifier of the file to retrieve. |

---

## Responses

### Success Response
| Status Code | Description                                      |
|-------------|--------------------------------------------------|
| `200 OK`    | File successfully retrieved.                    |

#### Example Response
```json
{
    "status": "success",
    "message": "File found",
    "data": {
        "id": "12345",
        "name": "Sample File",
        "url": "https://example.com/file.pdf",
        "created_at": "2025-04-01T12:00:00",
        "updated_at": "2025-04-06T12:00:00"
    }
}