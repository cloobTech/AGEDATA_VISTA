## Endpoint

`POST /auth/verify-email`

## Description

This endpoint is used to verify a user's email using a token and set a new password.

## Request

### Request Body

The request body should be a JSON object with the following structure:

| Field   | Type   | Required | Description                                |
| ------- | ------ | -------- | ------------------------------------------ |
| `token` | string | Yes      | The token provided for email verification. |

### Example Request Body

```json
{
  "token": "531079"
}
```
