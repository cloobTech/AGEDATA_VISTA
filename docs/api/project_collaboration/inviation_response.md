## Endpoint

`POST /api/v1/projects/{project_id}/invitation-response`

## Description

This endpoint allows a user to accept or decline a project invitation.

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
| `user_ids`         | list   | Yes      | A list of user IDs to receive the notification.                             |
| `title`            | string | Yes      | The title of the notification.                                              |
| `notification_type`| string | Yes      | The type of notification (`project_invitation`).                            |
| `message`          | string | Yes      | The message content of the notification.                                    |
| `resource_id`      | string | Yes      | The ID of the resource associated with the notification (e.g., project ID). |

## Request
```json
{
  "invitation_id": "ab3c8aa8-baba-4570-b6a0-3b187ce8ecdc",
  "respondent_id": "2dc90e48-277a-439c-84c9-8ba4379a5e00",
  "response": "accepted",
  "user_ids": ["2dc90e48-277a-439c-84c9-8ba4379a5e00"],
  "title": "Notification Response",
  "notification_type": "project_invitation",
  "message": "I'm joining you guys",
  "resource_id": "969c5583-ad00-4283-9577-18a288a66519"
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
