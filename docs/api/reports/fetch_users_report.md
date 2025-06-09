# Fetch User's Reports API

**Endpoint:**  
`GET /api/v1/reports/`

**Description:**  
Fetch all reports for a specific user, optionally filtered by `analysis_group`.

---

## Query Parameters

| Parameter        | Type   | Required | Description                                      |
|------------------|--------|----------|--------------------------------------------------|
| `user_id`        | `str`  | Yes      | The ID of the user whose reports are to be fetched. |
| `analysis_group` | `str`  | No       | Filter reports by the specified analysis group. |

---

## Response

### Success Response

**Status Code:** `200 OK`  
**Response Body:**
```json
{
    "status": "success",
    "message": "Reports retrieved successfully",
    "data": [
        {
            "id": "report_1",
            "title": "Sample Report",
            "analysis_group": "time_series",
            "created_at": "2023-06-01T12:00:00Z"
        },
        {
            "id": "report_2",
            "title": "Another Report",
            "analysis_group": "classification",
            "created_at": "2023-06-02T12:00:00Z"
        }
    ]
}
```

---

### Error Responses

**Status Code:** `404 Not Found`  
**Response Body:**
```json
{
    "detail": "User not found"
}
```

**Status Code:** `500 Internal Server Error`  
**Response Body:**
```json
{
    "detail": "An unexpected error occurred"
}
```

---

## Example Request

### Request URL:
```http
GET /api/v1/reports/?user_id=12345&analysis_group=time_series
```

### Example Response:
```json
{
    "status": "success",
    "message": "Reports retrieved successfully",
    "data": [
        {
            "id": "report_1",
            "title": "Sample Report",
            "analysis_group": "time_series",
            "created_at": "2023-06-01T12:00:00Z"
        }
    ]
}
```