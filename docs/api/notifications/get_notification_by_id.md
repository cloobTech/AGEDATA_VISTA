## Endpoint

`GET /api/v1/notifications/{notification_id}`

## Description

Retrieve a notification by its ID.

## Request

### URL Parameters

| Name              | Type   | Required | Description                     |
| ----------------- | ------ | -------- | ------------------------------- |
| `notification_id` | string | Yes      | The ID of the notification.     |

### Headers

| Name            | Type   | Required | Description                     |
| --------------- | ------ | -------- | ------------------------------- |
| `Content-Type`  | string | Yes      | Must be `application/json`.     |
| `Accept`        | string | Yes      | Must be `application/json`.     |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the notification details.

```json
{
  "status": "success",
  "message": "Notification retrieved successfully",
  "data": {
    "notification_id": "abc123",
    "title": "Project Invitation",
    "message": "You have been invited to join the project.",
    "notification_type": "project_invitation",
    "resource_id": "12345",
    "created_at": "2025-07-01T12:00:00Z"
  }
}
```

### Error Responses

- **Status Code:** `404 Not Found`
- **Body:** A JSON object indicating the notification was not found.

```json
{
  "detail": "Notification not found"
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
curl -X GET "http://localhost:8000/api/v1/notifications/abc123" -H "accept: application/json"
```