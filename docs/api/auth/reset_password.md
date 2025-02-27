## Endpoint

`PUT /auth/reset-password`

## Description

This endpoint is used to reset a user's password using a token and the new password.

## Request

### Request Body

The request body should be a JSON object with the following structure:

| Field           | Type   | Required | Description                            |
| --------------- | ------ | -------- | -------------------------------------- |
| `token`         | string | Yes      | The token provided for password reset. |
| `meta`          | object | Yes      | Contains the new password.             |
| `meta.password` | string | Yes      | The new password for the user.         |

### Example Request Body

```json
{
  "token": "788380",
  "meta": {
    "password": "newyourpassword"
  }
}
```

### Response

```json
{
  "status": "success",
  "message": "Password Reset Successful",
  "data": {}
}
```
