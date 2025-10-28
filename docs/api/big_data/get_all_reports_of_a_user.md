## Endpoint

`GET /api/v1/analysis/big-data/reports`

## Description

This endpoint retrieves a list of all big data reports for the currently authenticated user.

## Request

### Headers

| Name            | Type   | Required | Description                           |
| --------------- | ------ | -------- | ------------------------------------- |
| `Authorization` | string | Yes      | Bearer token for user authentication. |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing a list of big data reports.

```json
{
    "status": "success",
    "message": "Big data reports retrieved successfully",
    "data": [
        {
            "report_id": "70f422e1-c593-4062-a7f4-e9a33ac927a3",
            "name": "Sales Analysis Report",
            "description": "Analysis of sales data for Q1 2025",
            "created_at": "2025-10-01T12:00:00Z",
            "updated_at": "2025-10-02T15:30:00Z",
            "status": "COMPLETED",
            "user_id": "9c6ab8a3-543e-41a5-a93d-1c23456aeba4"
        },
        {
            "report_id": "81f422e1-c593-4062-a7f4-e9a33ac927b4",
            "name": "Revenue Analysis Report",
            "description": "Analysis of revenue data for Q2 2025",
            "created_at": "2025-10-05T10:00:00Z",
            "updated_at": "2025-10-06T14:00:00Z",
            "status": "PROCESSING",
            "user_id": "9c6ab8a3-543e-41a5-a93d-1c23456aeba4"
        }
    ]
}
```

### Error Response

- **Status Code:** `404 Not Found`
  - **Detail:** No reports found for the user.
  - **Example:**
    ```json
    {
        "detail": "No big data reports found for the user."
    }
    ```

- **Status Code:** `500 Internal Server Error`
  - **Detail:** Failed to retrieve the reports.
  - **Example:**
    ```json
    {
        "detail": "Failed to list big data reports: <error_message>"
    }
    ```

## Example Request

```sh
curl -X GET "http://localhost:8000/api/v1/analysis/big-data/reports" \
-H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Example Success Response

```json
{
    "status": "success",
    "message": "Big data reports retrieved successfully",
    "data": [
        {
            "report_id": "70f422e1-c593-4062-a7f4-e9a33ac927a3",
            "name": "Sales Analysis Report",
            "description": "Analysis of sales data for Q1 2025",
            "created_at": "2025-10-01T12:00:00Z",
            "updated_at": "2025-10-02T15:30:00Z",
            "status": "COMPLETED",
            "user_id": "9c6ab8a3-543e-41a5-a93d-1c23456aeba4"
        }
    ]
}
```

## Example Error Response

```json
{
    "detail": "No big data reports found for the user."
}
```