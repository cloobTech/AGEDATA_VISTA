## Endpoint

`GET /api/v1/subscriptions/active`

## Description

Retrieve the currently active subscription for the logged-in user.

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
- **Body:** A JSON object containing the details of the user's active subscription.

```json
{
  "status": "success",
  "message": "Active subscription retrieved successfully",
  "data": {
    "start_date": "2025-09-20T17:59:13.126818Z",
    "end_date": "2025-10-20T17:59:13.126818Z",
    "payment_info": {
      "paystack_reference": "v2nsmhrfuh",
      "amount": 70000.0,
      "paid_at": "2025-09-20T17:59:11.000Z",
      "channel": "card",
      "currency": "NGN"
    },
    "created_at": "2025-09-20T17:59:13.126890Z",
    "plan_id": "9ed8a0a9-0b42-4bb1-889a-9228993f7a45",
    "user_id": "9c6ab8a3-543e-41a5-a93d-1c23456aeba4",
    "status": "active",
    "id": "946098c3-a432-45a5-abb7-367a078eba42",
    "updated_at": "2025-09-20T17:59:13.126940Z",
    "plan": {
      "duration_days": 30,
      "id": "9ed8a0a9-0b42-4bb1-889a-9228993f7a45",
      "updated_at": "2025-09-20T10:59:08.573874Z",
      "price": 70000.0,
      "name": "Premium",
      "created_at": "2025-09-20T10:18:16.359761Z"
    }
  }
}
```

### Error Responses

- **Status Code:** `404 Not Found`
  - **Detail:** No active subscription found for the user.
  - **Example:**
    ```json
    {
      "detail": "Active subscription not found"
    }
    ```

- **Status Code:** `401 Unauthorized`
  - **Detail:** User is not authenticated.
  - **Example:**
    ```json
    {
      "detail": "Could not validate credentials"
    }
    ```

---

## Example Request

```sh
curl -X GET "http://localhost:8000/api/v1/subscriptions/active" \
-H "Authorization: Bearer <ACCESS_TOKEN>" \
-H "Content-Type: application/json"
```

## Example Success Response

```json
{
  "status": "success",
  "message": "Active subscription retrieved successfully",
  "data": {
    "start_date": "2025-09-20T17:59:13.126818Z",
    "end_date": "2025-10-20T17:59:13.126818Z",
    "payment_info": {
      "paystack_reference": "v2nsmhrfuh",
      "amount": 70000.0,
      "paid_at": "2025-09-20T17:59:11.000Z",
      "channel": "card",
      "currency": "NGN"
    },
    "created_at": "2025-09-20T17:59:13.126890Z",
    "plan_id": "9ed8a0a9-0b42-4bb1-889a-9228993f7a45",
    "user_id": "9c6ab8a3-543e-41a5-a93d-1c23456aeba4",
    "status": "active",
    "id": "946098c3-a432-45a5-abb7-367a078eba42",
    "updated_at": "2025-09-20T17:59:13.126940Z",
    "plan": {
      "duration_days": 30,
      "id": "9ed8a0a9-0b42-4bb1-889a-9228993f7a45",
      "updated_at": "2025-09-20T10:59:08.573874Z",
      "price": 70000.0,
      "name": "Premium",
      "created_at": "2025-09-20T10:18:16.359761Z"
    }
  }
}
```