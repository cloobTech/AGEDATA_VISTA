## Endpoint

`GET /api/v1/users`

## Description

This endpoint retrieves all users.


## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the following keys:

```json
{
  "status": "success",
  "message": "Users found",
  "data": [
    {
      "id": "string",
      "name": "string",
      "email": "string",
      "created_at": "string",
      "updated_at": "string"
    },
    ...
  ]
}