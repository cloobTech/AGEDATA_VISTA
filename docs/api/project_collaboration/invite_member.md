## Endpoint

`POST /api/v1/projects/{project_id}/invitation`

## Description

This endpoint sends a project invitation to a user. The invitation can be sent to an existing user or to an email address if the user is not registered.

## Request

The request should be made with `Content-Type: application/json` and include the following parameters:

### URL Parameters

| Name         | Type   | Required | Description                |
| ------------ | ------ | -------- | -------------------------- |
| `project_id` | string | Yes      | The ID of the project.     |

### JSON Body Parameters

| Name            | Type   | Required | Description                                      |
| --------------- | ------ | -------- | ------------------------------------------------ |
| `user_id`       | string | No       | The ID of the user to invite (if user exists).   |
| `email`         | string | No       | The email of the user to invite (if not registered). |
| `acting_user_id`| string | Yes      | The ID of the user sending the invitation.       |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the following keys:

```json
{
  "status": "success",
  "message": "Project invitation sent",
  "data": {
    "invitation_id": "string"
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
  "user_id": "67890",
  "acting_user_id": "11223"
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