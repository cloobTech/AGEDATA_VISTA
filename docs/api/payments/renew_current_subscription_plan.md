## Endpoint

`POST /api/v1/subscriptions/renew`

## Description

Renew existing plan. This endpoint generates a Paystack checkout link for the user to complete the payment.

## Request

### Headers

| Name            | Type   | Required | Description                     |
| --------------- | ------ | -------- | ------------------------------- |
| `Authorization` | string | Yes      | Bearer token for user authentication. |
| `Content-Type`  | string | Yes      | Must be `application/json`.     |
| `Accept`        | string | Yes      | Must be `application/json`.     |



## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the Paystack checkout link and payment reference.

```json
{
  "authorization_url": "https://checkout.paystack.com/abc123xyz",
  "reference": "v2nsmhrfuh"
}
```

### Error Responses

- **Status Code:** `404 Not Found`
  - **Detail:** Plan not found.
  - **Example:**
    ```json
    {
      "detail": "Plan not found"
    }
    ```

- **Status Code:** `400 Bad Request`
  - **Detail:** Failed to initialize payment.
  - **Example:**
    ```json
    {
      "detail": "Failed to initialize payment"
    }
    ```

---

## Example Request

```sh
curl -X POST "http://localhost:8000/api/v1/subscriptions/renew" \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-H "Content-Type: application/json" \

```

## Example Success Response

```json
{
  "authorization_url": "https://checkout.paystack.com/abc123xyz",
  "reference": "v2nsmhrfuh"
}
```