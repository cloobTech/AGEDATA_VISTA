# API Route: `PUT /api/v1/file-upload/{file_id}`

## Description
Updates a file object by its unique identifier. This route allows users to update specific attributes of the file, such as the `name` attribute.

---

## Endpoint

| Method | URL                              | Description              |
|--------|----------------------------------|--------------------------|
| `PUT`  | `/api/v1/file-upload/{file_id}`  | Updates a file by its ID. |

---

## Parameters

### Path Parameters
| Name       | Type   | Required | Description                     |
|------------|--------|----------|---------------------------------|
| `file_id`  | `str`  | Yes      | The unique identifier of the file to update. |

### Request Body
| Name       | Type   | Required | Description                     |
|------------|--------|----------|---------------------------------|
| `data`     | `dict` | Yes      | A dictionary containing the attributes to update (e.g., `name`). |

---

## Responses

### Success Response
| Status Code | Description                                      |
|-------------|--------------------------------------------------|
| `200 OK`    | File successfully updated.                      |

#### Example Response
```json
{
    "status": "success",
    "message": "File updated",
    "data": {
        "id": "12345",
        "name": "Updated File Name",
        "url": "https://example.com/file.pdf",
        "created_at": "2025-04-01T12:00:00",
        "updated_at": "2025-04-06T12:00:00"
    }
}