## Endpoint

`GET /api/v1/plans/{plan_id}`

## Description

Retrieve a specific subscription plan by its ID.

## Request

### URL Parameters

| Name      | Type   | Required | Description                     |
| --------- | ------ | -------- | ------------------------------- |
| `plan_id` | string | Yes      | The ID of the subscription plan.|

### Headers

| Name            | Type   | Required | Description                     |
| --------------- | ------ | -------- | ------------------------------- |
| `Content-Type`  | string | Yes      | Must be `application/json`.     |
| `Accept`        | string | Yes      | Must be `application/json`.     |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the details of the subscription plan.

```json
{
  "status": "success",
  "message": "Plan found",
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

- **Status Code:** `404 Not Found`
  - **Detail:** Plan not found.
  - **Example:**
    ```json
    {
      "detail": "Plan not found"
    }
    ```

---

## Example Requests

### Get All Plans
```sh
curl -X GET "http://localhost:8000/api/v1/plans" -H "accept: application/json"
```

### Get Plan by ID
```sh
curl -X GET "http://localhost:8000/api/v1/plans/5d4a3d81-f981-4c86-8c20-4b34a16e6e05" -H "accept: application/json"
```