## Endpoint

`GET /api/v1/plans`

## Description

Retrieve all subscription plans.

## Request

### Headers

| Name            | Type   | Required | Description                     |
| --------------- | ------ | -------- | ------------------------------- |
| `Content-Type`  | string | Yes      | Must be `application/json`.     |
| `Accept`        | string | Yes      | Must be `application/json`.     |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the list of all subscription plans.

```json
{
  "status": "success",
  "message": "Plans found",
  "data": [
    {
      "price": 30000,
      "name": "PRO",
      "created_at": "2025-09-20T10:14:10.663358Z",
      "duration_days": 30,
      "id": "5d4a3d81-f981-4c86-8c20-4b34a16e6e05",
      "updated_at": "2025-09-20T10:59:59.394097Z",
      "_class_": "Plan"
    },
    {
      "price": 15000,
      "name": "BASIC",
      "created_at": "2025-09-19T09:00:00.000000Z",
      "duration_days": 15,
      "id": "7a2b3c4d-1234-5678-9101-112131415161",
      "updated_at": "2025-09-19T09:30:00.000000Z",
      "_class_": "Plan"
    }
  ]
}
```