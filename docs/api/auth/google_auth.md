## Endpoint

`POST /api/v1/auth/google-auth`

## Description

Authenticate a user via Google credentials using the `@react-oauth/google` library. If the user exists, they are logged in. If the user does not exist, a new account is created.

## Request

### Headers

| Name           | Type   | Required | Description                 |
| -------------- | ------ | -------- | --------------------------- |
| `Content-Type` | string | Yes      | Must be `application/json`. |
| `Accept`       | string | Yes      | Must be `application/json`. |

### JSON Body Parameters

| Name         | Type   | Required | Description                                     |
| ------------ | ------ | -------- | ----------------------------------------------- |
| `credential` | string | Yes      | The Google ID token obtained from the frontend. |

### Example Request

```json
{
  "credential": "<GOOGLE_ID_CREDENTIAL>"
}
```

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing access and refresh tokens.

```json
{
  "access_token": "<ACCESS_TOKEN>",
  "refresh_token": "<REFRESH_TOKEN>"
}
```

### Error Responses

- **Status Code:** `400 Bad Request`

  - **Detail:** Missing or invalid Google credential.
  - **Example:**
    ```json
    {
      "detail": "Missing Google credential"
    }
    ```

- **Status Code:** `400 Bad Request`

  - **Detail:** Google account does not provide an email.
  - **Example:**
    ```json
    {
      "detail": "Google account does not provide an email"
    }
    ```

- **Status Code:** `500 Internal Server Error`
  - **Detail:** Unexpected error during authentication.
  - **Example:**
    ```json
    {
      "detail": "Unexpected error: <error_message>"
    }
    ```

## Example Request

```sh
curl -X POST "http://localhost:8000/api/v1/auth/google-auth" \
-H "Content-Type: application/json" \
-d '{
  "credential": "<GOOGLE_ID_TOKEN>"
}'
```

## Example Success Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
