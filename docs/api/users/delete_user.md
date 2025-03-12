## Endpoint

`DELETE /api/v1/users/{user_id}`

## Description

This endpoint deletes an existing user.

## Request

The request should be made with `Content-Type: application/json` and include the following parameters:

### URL Parameters

| Name      | Type   | Required | Description                |
| --------- | ------ | -------- | -------------------------- |
| `user_id` | string | Yes      | The ID of the user.        |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the following keys:

```json
{
  "status": "success",
  "message": "User deleted",
  "data": {
  }
}