## Endpoint

`POST /api/v1/projects/{project_id}/invitation`

## Description

This endpoint sends a project invitation to multiple users. The invitation can be sent to existing users or to an email address if the user is not registered.

## Request

The request should be made with `Content-Type: application/json` and include the following parameters:

### URL Parameters

| Name         | Type   | Required | Description            |
| ------------ | ------ | -------- | ---------------------- |
| `project_id` | string | Yes      | The ID of the project. |

### JSON Body Parameters

| Name                | Type   | Required | Description                                                                                                |
| ------------------- | ------ | -------- | ---------------------------------------------------------------------------------------------------------- |
| `acting_user_id`    | string | Yes      | The ID of the user performing the operation (sending out the invite).                                      |
| `user_ids`          | list   | Yes      | A list of user IDs to receive the notification.                                                            |
| `title`             | string | Yes      | The title of the notification.                                                                             |
| `notification_type` | string | Yes      | The type of notification (`project_invitation`).                                                           |
| `message`           | string | Yes      | The message content of the notification.                                                                   |
| `resource_id`       | string | Yes      | The ID of the resource associated with the notification (e.g., project ID).                                |
| `role`              | string | NO       | The role of the intended new member (`viewer, editor or admin`) by default a new member is set to `viewer` |
| `email      `       | string | NO       | Optional for cases where the user isn't a platform member yet...                                           |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the following keys:

```json
{
  "status": "success",
  "message": "Project invitation sent",
  "data": {
    "invitation_id": "abc123"
  }
}
```

### Error Responses

- **Status Code:** `403 Forbidden`
- **Body:** A JSON object containing the following keys:

```json
{
  "detail": "Permission denied. Only an owner or admin can send invitations"
}
```

- **Status Code:** `404 Not Found`
- **Body:** A JSON object containing the following keys:

```json
{
  "detail": "Project not found"
}
```

- **Status Code:** `409 Conflict`
- **Body:** A JSON object containing the following keys:

```json
{
  "detail": "User is already a project member"
}
```

- **Status Code:** `409 Conflict`
- **Body:** A JSON object containing the following keys:

```json
{
  "detail": "User already has a pending invitation"
}
```

### Example Request

```sh
curl -X POST "http://localhost:8000/api/v1/projects/12345/invitation" -H "accept: application/json" -H "Content-Type: application/json" -d '{
  "invitation_id": "ab3c8aa8-baba-4570-b6a0-3b187ce8ecdc",
  "user_id": "2dc90e48-277a-439c-84c9-8ba4379a5e00",
  "response": "accepted",
  "user_ids": ["2dc90e48-277a-439c-84c9-8ba4379a5e00"],
  "title": "Notification Response",
  "notification_type": "project_invitation",
  "message": "I'm joining you guys",
  "resource_id": "969c5583-ad00-4283-9577-18a288a66519"
}'
```

### Example Success Response

```json
{
  "status": "success",
  "message": "Project invitation sent",
  "data": {
    "invitation_id": "abc123"
  }
}
```

### Example Error Response

```json
{
  "detail": "Project not found"
}
```
