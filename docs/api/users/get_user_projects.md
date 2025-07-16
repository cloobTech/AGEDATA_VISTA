## Endpoint

`GET /api/v1/users/{user_id}/projects`

## Description

Retrieve all projects associated with a specific user.

## Request

### URL Parameters

| Name      | Type   | Required | Description                                            |
| --------- | ------ | -------- | ------------------------------------------------------ |
| `user_id` | string | Yes      | The ID of the user whose projects are being retrieved. |

### Headers

| Name           | Type   | Required | Description                 |
| -------------- | ------ | -------- | --------------------------- |
| `Content-Type` | string | Yes      | Must be `application/json`. |
| `Accept`       | string | Yes      | Must be `application/json`. |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the user's projects.

```json
{
  "status": "success",
  "message": "Projects retrieved successfully",
  "data": [
    {
      "project_id": "abc123",
      "name": "Project Alpha",
      "description": "A sample project",
      "created_at": "2025-07-01T12:00:00Z",
      "updated_at": "2025-07-02T12:00:00Z"
    },
    {
      "project_id": "def456",
      "name": "Project Beta",
      "description": "Another sample project",
      "created_at": "2025-07-03T12:00:00Z",
      "updated_at": "2025-07-04T12:00:00Z"
    }
  ]
}
```

### Error Responses

- **Status Code:** `500 Internal Server Error`
- **Body:** A JSON object indicating an unexpected error occurred.

```json
{
  "detail": "An unexpected error occurred"
}
```

## Example Request

```sh
curl -X GET "http://localhost:8000/api/v1/users/abc123/projects" -H "accept: application/json"
```
