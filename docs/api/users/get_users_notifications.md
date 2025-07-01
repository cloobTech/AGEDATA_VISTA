## Endpoint

`GET /api/v1/users/{user_id}/notifications`

## Description

Retrieve all notifications for a specific user.

## Request

### URL Parameters

| Name      | Type   | Required | Description                                                 |
| --------- | ------ | -------- | ----------------------------------------------------------- |
| `user_id` | string | Yes      | The ID of the user whose notifications are being retrieved. |

### Headers

| Name           | Type   | Required | Description                 |
| -------------- | ------ | -------- | --------------------------- |
| `Content-Type` | string | Yes      | Must be `application/json`. |
| `Accept`       | string | Yes      | Must be `application/json`. |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the user's notifications.

```json
{
  "status": "success",
  "message": "Notifications retrieved successfully",
  "data": [
    {
      "notification_id": "abc123",
      "title": "Project Invitation",
      "message": "You have been invited to join the project.",
      "notification_type": "project_invitation",
      "resource_id": "12345",
      "created_at": "2025-07-01T12:00:00Z"
    },
    {
      "notification_id": "def456",
      "title": "Task Assigned",
      "message": "You have been assigned a new task.",
      "notification_type": "task_assignment",
      "resource_id": "67890",
      "created_at": "2025-07-01T13:00:00Z"
    }
  ]
}
```

### Error Responses

- **Status Code:** `409 Conflict`
- **Body:** A JSON object indicating the user was not found.

```json
{
  "detail": "User not found"
}
```

- **Status Code:** `500 Internal Server Error`
- **Body:** A JSON object indicating an unexpected error occurred.

```json
{
  "detail": "An unexpected error occurred"
}
```

## Example Request

```sh
curl -X GET "http://localhost:8000/api/v1/users/abc123/notifications" -H "accept: application/json"
```
