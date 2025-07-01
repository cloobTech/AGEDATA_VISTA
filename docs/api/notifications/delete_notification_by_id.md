## Endpoint

`DELETE /api/v1/notifications/{notification_id}`

## Description

Delete a notification by its ID.

## Request

### URL Parameters

| Name              | Type   | Required | Description                     |
| ----------------- | ------ | -------- | ------------------------------- |
| `notification_id` | string | Yes      | The ID of the notification to delete. |

### Headers

| Name            | Type   | Required | Description                     |
| --------------- | ------ | -------- | ------------------------------- |
| `Content-Type`  | string | Yes      | Must be `application/json`.     |
| `Accept`        | string | Yes      | Must be `application/json`.     |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object confirming the deletion of the notification.

```json
{
  "status": "success",
  "message": "Notification deleted successfully",
  "data": {
    "notification_id": "abc123"
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
curl -X DELETE "http://localhost:8000/api/v1/notifications/abc123" -H "accept: application/json"
```