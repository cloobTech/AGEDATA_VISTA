## Endpoint

`POST /api/v1/projects/{project_id}/invitation-response`

## Description

This endpoint allows a user to accept or decline a project invitation.

## Request

### URL Parameters

| Name         | Type   | Required | Description                |
| ------------ | ------ | -------- | -------------------------- |
| `project_id` | string | Yes      | The ID of the project.     |


The request should be made with `Content-Type: application/json` and include the following parameters:

### JSON Body Parameters

| Name            | Type   | Required | Description                                      |
| --------------- | ------ | -------- | ------------------------------------------------ |
| `invitation_id` | string | Yes      | The ID of the project invitation.                |
| `user_id`       | string | Yes      | The ID of the user responding to the invitation. |
| `response`      | string | Yes      | The response to the invitation ("accepted" or "declined"). |

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