## Endpoint

`PUT /api/v1/notifications/{notification_id}`

## Description

Update a notification's status. The user must provide the `is_read` status and their `user_id`.

## Request

### URL Parameters

| Name              | Type   | Required | Description                     |
| ----------------- | ------ | -------- | ------------------------------- |
| `notification_id` | string | Yes      | The ID of the notification to update. |

### JSON Body Parameters

`Note: this are the only allowed fields and they are both mandatory`

| Name      | Type    | Required | Description                              |
| --------- | ------- | -------- | ---------------------------------------- |
| `is_read` | boolean | Yes      | Indicates whether the notification has been read. |
| `user_id` | string  | Yes      | The ID of the user updating the notification. |

### Headers

| Name            | Type   | Required | Description                     |
| --------------- | ------ | -------- | ------------------------------- |
| `Content-Type`  | string | Yes      | Must be `application/json`.     |
| `Accept`        | string | Yes      | Must be `application/json`.     |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object confirming the update of the notification.

```json
{
  "status": "success",
  "message": "Notification updated successfully",
  "data": {
    "notification_id": "abc123",
    "is_read": true,
    "user_id": "2dc90e48-277a-439c-84c9-8ba4379a5e00"
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

- **Status Code:** `400 Bad Request`
- **Body:** A JSON object indicating missing or invalid data.

```json
{
  "detail": "Required fields are missing or invalid"
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
curl -X PUT "http://localhost:8000/api/v1/notifications/abc123" -H "accept: application/json" -H "Content-Type: application/json" -d '{
  "is_read": true,
  "user_id": "2dc90e48-277a-439c-84c9-8ba4379a5e00"
}'
```

## Example Success Response

```json
{
  "status": "success",
  "message": "Notification updated successfully",
  "data": {
    "notification_id": "abc123",
    "is_read": true,
    "user_id": "2dc90e48-277a-439c-84c9-8ba4379a5e00"
  }
}
```