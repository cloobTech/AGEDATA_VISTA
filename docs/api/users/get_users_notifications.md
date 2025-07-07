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
      "status": "success",
      "message": "User's notifications fetched successfully",
      "data": [
        {
          "message": "Please Join us again oooo",
          "title": "Another Notification",
          "resource_id": "5ff7934b-352e-48f2-976b-5154192a5e0e",
          "id": "b5346ddf-2dfc-4ea3-a7c9-64d9c4236f56",
          "updated_at": "2025-07-04T20:58:44.727463Z",
          "notification_type": "project_invitation",
          "sender_id": "9bed01f0-0c94-441c-960d-457800405da3",
          "created_at": "2025-07-04T20:58:44.727460Z",
          "sender": {
            "id": "9bed01f0-0c94-441c-960d-457800405da3",
            "email": "belkid98@gmail.com",
            "first_name": "John",
            "last_name": "Doe",
            "profile_picture": null
          },
          "_class_": "Notification",
          "is_read": false,
          "recipient_user": {
            "id": "ea5a5322-2487-4f70-a009-42226b6471e1",
            "email": "third_user@gmail.com",
            "first_name": "Olamide",
            "last_name": "Bello",
            "profile_picture": null
          }
        }
      ]
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
