## Endpoint

`POST /api/v1/plans`

## Description

Create a new subscription plan.

## Request

### Headers

| Name            | Type   | Required | Description                     |
| --------------- | ------ | -------- | ------------------------------- |
| `Content-Type`  | string | Yes      | Must be `application/json`.     |
| `Accept`        | string | Yes      | Must be `application/json`.     |

### JSON Body Parameters

| Name           | Type   | Required | Description                              |
| -------------- | ------ | -------- | ---------------------------------------- |
| `price`        | number | Yes      | The price of the subscription plan.      |
| `name`         | string | Yes      | The name of the subscription plan.       |
| `duration_days`| number | Yes      | The duration of the plan in days.        |

### Example Request

```json
{
  "price": 30000,
  "name": "PRO",
  "duration_days": 30
}
```

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the details of the created plan.

```json
{
  "status": "success",
  "message": "Plan created successfully",
  "data": {
    "price": 30000,
    "name": "PRO",
    "created_at": "2025-09-20T10:14:10.663358Z",
    "duration_days": 30,
    "id": "5d4a3d81-f981-4c86-8c20-4b34a16e6e05",
    "updated_at": "2025-09-20T10:59:59.394097Z",
    "_class_": "Plan"
  }
}
```

### Error Responses

- **Status Code:** `400 Bad Request`
  - **Detail:** Missing or invalid data.
  - **Example:**
    ```json
    {
      "detail": "Must provide data to create a plan"
    }
    ```

- **Status Code:** `500 Internal Server Error`
  - **Detail:** Unexpected error during plan creation.
  - **Example:**
    ```json
    {
      "detail": "An unexpected error occurred"
    }
    ```

## Example Request

```sh
curl -X POST "http://localhost:8000/api/v1/plans" \
-H "Content-Type: application/json" \
-d '{
  "price": 30000,
  "name": "PRO",
  "duration_days": 30
}'
```

## Example Success Response

```json
{
  "status": "success",
  "message": "Plan created successfully",
  "data": {
    "price": 30000,
    "name": "PRO",
    "created_at": "2025-09-20T10:14:10.663358Z",
    "duration_days": 30,
    "id": "5d4a3d81-f981-4c86-8c20-4b34a16e6e05",
    "updated_at": "2025-09-20T10:59:59.394097Z",
    "_class_": "Plan"
  }
}
```