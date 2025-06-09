# Get Report by ID API

**Endpoint:**  
`GET /api/v1/reports/{report_id}`

**Description:**  
Fetch a single report by its unique ID.

---

## Path Parameters

| Parameter   | Type   | Required | Description                     |
|-------------|--------|----------|---------------------------------|
| `report_id` | `str`  | Yes      | The unique ID of the report to fetch. |

---

## Response

### Success Response

**Status Code:** `200 OK`  
**Response Body:**
```json
{
    "status": "success",
    "message": "Report found",
    "data": {
        "id": "report_1",
        "title": "Sample Report",
        "analysis_group": "time_series",
        "created_at": "2023-06-01T12:00:00Z"
    }
}
```

---

### Error Responses

**Status Code:** `404 Not Found`  
**Response Body:**
```json
{
    "detail": "Report not found"
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
GET /api/v1/reports/report_1
```

### Example Response:
```json
{
    "status": "success",
    "message": "Report found",
    "data": {
        "id": "report_1",
        "title": "Sample Report",
        "analysis_group": "time_series",
        "created_at": "2023-06-01T12:00:00Z"
    }
}
```