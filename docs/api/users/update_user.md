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

| Name               | Type    | Required | Description                                   |
| ------------------ | ------- | -------- | --------------------------------------------- |
| `first_name`       | string  | No       | The first name of the user.                  |
| `last_name`        | string  | No       | The last name of the user.                   |
| `secondary_email`  | string  | No       | A secondary email address for the user.      |
| `salutation`       | string  | No       | The salutation (e.g., Mr., Ms.) of the user. |
| `organization_role`| string  | No       | The role of the user in their organization.  |
| `corporate_name`   | string  | No       | The corporate name associated with the user. |

---

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
    "first_name": "string",
    "last_name": "string",
    "secondary_email": "string",
    "salutation": "string",
    "organization_role": "string",
    "profile_picture": "string",
    "corporate_name": "string",
    "email_verified": true,
    "reset_token": "string",
    "disabled": false,
    "role": "string",
    "token_created_at": "string",
    "created_at": "string",
    "updated_at": "string"
  }
}
```