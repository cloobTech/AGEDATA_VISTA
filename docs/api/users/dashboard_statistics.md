## Endpoint

`GET /api/v1/users/{user_id}/statistics`

## Description

Retrieve report statistics for a specific user.

## Request

### URL Parameters

| Name      | Type   | Required | Description                                                     |
| --------- | ------ | -------- | --------------------------------------------------------------- |
| `user_id` | string | Yes      | The ID of the user whose report statistics are being retrieved. |

### Headers

| Name           | Type   | Required | Description                 |
| -------------- | ------ | -------- | --------------------------- |
| `Content-Type` | string | Yes      | Must be `application/json`. |
| `Accept`       | string | Yes      | Must be `application/json`. |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the user's report statistics.

```json
{
  "status": "success",
  "message": "User's statistics fetched successfully",
  "data": {
    "total_reports": 3,
    "breakdown": [
      {
        "analysis_group": "advance",
        "count": 1
      },
      {
        "analysis_group": "descriptive",
        "count": 2
      }
    ]
  }
}
```

### Error Responses

- **Status Code:** `409 Conflict`
- **Body:** A JSON object indicating the user was not found.

```json
{
  "detail": "User not found"
}
```

- **Status Code:** `500 Internal Server Error`
- **Body:** A JSON object indicating an unexpected error occurred.

```json
{
  "detail": "An unexpected error occurred"
}
```

## Example Request

```sh
curl -X GET "http://localhost:8000/api/v1/users/abc123/statistics" -H "accept: application/json"
```
