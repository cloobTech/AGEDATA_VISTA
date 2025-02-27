## Endpoint

```
POST /auth/register
```

## Description
This endpoint is used to register a new user in the system. It collects the user's profile details and authentication details.

## Request

### Request Body
The request body should be a JSON object with the following structure:

| Field           | Type     | Required | Description                                    |
|----------------|----------|----------|------------------------------------------------|
| `email`        | string   | Yes      | The email address of the user.                 |
| `password`     | string   | Yes      | The password for authentication.               |
| `first_name`   | string   | Yes      | The first name of the user.                    |
| `last_name`    | string   | Yes      | The last name of the user.                     |
| `corporate_name` | string  | No       | The corporate name, if applicable.             |
| `email_verified` | boolean | No       | Indicates if the email is verified. Defaults to `false`. |
| `reset_token`  | string   | No       | Token for resetting the password.              |

### Example Request Body

```json
{
  "email": "johndoe@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "corporate_name": "Tech Corp",
  "email_verified": false,
  "reset_token": null
}
```

## Response

### Success Response

- **Status Code:** `201 Created`
- **Body:**

```json
{
  "status": "success",
  "message": "User registered successfully",
  "data": {
    "email": "johndoe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "corporate_name": "Tech Corp",
    "email_verified": false
  }
}
```

### Error Responses

#### Missing Required Fields

- **Status Code:** `400 Bad Request`
- **Body:**

```json
{
  "status": "error",
  "message": "Missing required fields: email, password, first_name, last_name"
}
```

#### Invalid Email Format

- **Status Code:** `400 Bad Request`
- **Body:**

```json
{
  "status": "error",
  "message": "Invalid email format"
}
```

#### User Already Exists

- **Status Code:** `409 Conflict`
- **Body:**

```json
{
  "status": "error",
  "message": "User with this email already exists"
}
```

