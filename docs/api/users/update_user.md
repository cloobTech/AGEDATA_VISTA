## Endpoint

`PUT /api/v1/users/{user_id}`

## Description

This endpoint updates the details of an existing user.

## Request

The request should be made with `Content-Type: application/json` and include the following parameters:

### URL Parameters

| Name      | Type   | Required | Description                |
| --------- | ------ | -------- | -------------------------- |
| `user_id` | string | Yes      | The ID of the user.        |

### JSON Body Parameters

| Name      | Type   | Required | Description                |
| --------- | ------ | -------- | -------------------------- |
| `name`    | string | No       | The new name of the user.  |

NOTE: There might be no need to want to update the user object like this but if there is, you may follow the pattern above


## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the following keys:

```json
{
  "status": "success",
  "message": "User updated",
  "data": {
    "id": "string",
    "name": "string",
    "email": "string",
    "created_at": "string",
    "updated_at": "string"
  }
}