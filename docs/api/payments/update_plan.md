## Endpoint

`PUT /api/v1/plans/{plan_id}`

## Description

Update an existing subscription plan.

## Request

### URL Parameters

| Name      | Type   | Required | Description                      |
| --------- | ------ | -------- | -------------------------------- |
| `plan_id` | string | Yes      | The ID of the subscription plan. |

### Headers

| Name           | Type   | Required | Description                 |
| -------------- | ------ | -------- | --------------------------- |
| `Content-Type` | string | Yes      | Must be `application/json`. |
| `Accept`       | string | Yes      | Must be `application/json`. |

### JSON Body Parameters

| Name            | Type   | Required | Description                                 |
| --------------- | ------ | -------- | ------------------------------------------- |
| `price`         | number | No       | The updated price of the subscription plan. |
| `name`          | string | No       | The updated name of the subscription plan.  |
| `duration_days` | number | No       | The updated duration of the plan in days.   |

### Example Request

```json
{
  "price": 35000,
  "name": "PRO+",
  "duration_days": 60
}
```

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the updated subscription plan details.

```json
{
  "status": "success",
  "message": "Plan updated successfully",
  "data": {
    "price": 35000,
    "name": "PRO+",
    "created_at": "2025-09-20T10:14:10.663358Z",
    "duration_days": 60,
    "id": "5d4a3d81-f981-4c86-8c20-4b34a16e6e05",
    "updated_at": "2025-09-20T11:30:00.000000Z",
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

- **Status Code:** `400 Bad Request`
  - **Detail:** Missing or invalid data.
  - **Example:**
    ```json
    {
      "detail": "Must provide data to update"
    }
    ```

---

## Example Requests

### Update Plan

```sh
curl -X PUT "http://localhost:8000/api/v1/plans/5d4a3d81-f981-4c86-8c20-4b34a16e6e05" \
-H "Content-Type: application/json" \
-d '{
  "price": 35000,
  "name": "PRO+",
  "duration_days": 60
}'
```

### Delete Plan

```sh
curl -X DELETE "http://localhost:8000/api/v1/plans/5d4a3d81-f981-4c86-8c20-4b34a16e6e05" \
-H "Content-Type: application/json"
```
