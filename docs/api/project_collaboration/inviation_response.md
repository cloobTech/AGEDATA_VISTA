## Endpoint

`POST /api/v1/projects/{project_id}/invitation-response`

## Description

This endpoint allows a user to accept or decline a project invitation and sends a notification to the relevant users.

## Request

### URL Parameters

| Name         | Type   | Required | Description            |
| ------------ | ------ | -------- | ---------------------- |
| `project_id` | string | Yes      | The ID of the project. |

The request should be made with `Content-Type: application/json` and include the following parameters:

### JSON Body Parameters

| Name               | Type   | Required | Description                                                                 |
| ------------------ | ------ | -------- | --------------------------------------------------------------------------- |
| `invitation_id`    | string | Yes      | The ID of the invitation being responded to.                                |
| `respondent_id`    | string | Yes      | The ID of the user responding to the invitation.                            |
| `response`         | string | Yes      | The response to the invitation (`accepted` or `declined`).                  |
| `sender_id`        | string | Yes      | The ID of the user sending the notification.                                |
| `user_ids`         | list   | Yes      | A list of user IDs to receive the notification.                             |
| `acting_user_id`   | string | Yes      | The ID of the user performing the operation (sending the notification).     |
| `title`            | string | Yes      | The title of the notification.                                              |
| `notification_type`| string | Yes      | The type of notification (`project_invitation`).                            |
| `message`          | string | Yes      | The message content of the notification.                                    |
| `resource_id`      | string | Yes      | The ID of the resource associated with the notification (e.g., project ID). |

## Example Request

```json
{
  "invitation_id": "ab3c8aa8-baba-4570-b6a0-3b187ce8ecdc",
  "respondent_id": "2dc90e48-277a-439c-84c9-8ba4379a5e00",
  "response": "accepted",
  "sender_id": "9bed01f0-0c94-441c-960d-457800405da3",
  "user_ids": ["ea5a5322-2487-4f70-a009-42226b6471e1"],
  "acting_user_id": "9bed01f0-0c94-441c-960d-457800405da3",
  "title": "Another Notification",
  "notification_type": "project_invitation",
  "message": "Please Join us again oooo",
  "resource_id": "5ff7934b-352e-48f2-976b-5154192a5e0e"
}
```

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the following keys:

```json
{
  "status": "success",
  "message": "Invitation accepted",
  "data": {}
}
```

### Error Responses

- **Status Code:** `400 Bad Request`
- **Body:** A JSON object indicating missing or invalid data.

```json
{
  "detail": "Required fields are missing or invalid"
}
```

- **Status Code:** `404 Not Found`
- **Body:** A JSON object indicating the project or invitation was not found.

```json
{
  "detail": "Project or invitation not found"
}
```

- **Status Code:** `500 Internal Server Error`
- **Body:** A JSON object indicating an unexpected error occurred.

```json
{
  "detail": "An unexpected error occurred"
}
```