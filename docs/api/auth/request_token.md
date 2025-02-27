# Request New Token Route Documentation

## Endpoint

`POST /auth/request-reset-token`

## Description

This endpoint allows a user to request a new token for resetting their password. The token will be sent to the provided email address.

## Request

### Request Body

The request body should be a JSON object with the following structure:

| Field   | Type   | Required | Description                                         |
| ------- | ------ | -------- | --------------------------------------------------- |
| `email` | string | Yes      | The email address of the user requesting the token. |

### Example Request Body

```json
{
  "email": "johndoe@example.com"
}
```

### Response

```json
{
  "status": "success",
  "message": "Token sent successfully",
  "data": {}
}
```
