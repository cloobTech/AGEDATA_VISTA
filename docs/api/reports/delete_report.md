# Delete Report by ID API

**Endpoint:**  
`DELETE /api/v1/reports/{report_id}`

**Description:**  
Delete a single report by its unique ID.

---

## Path Parameters

| Parameter   | Type   | Required | Description                     |
|-------------|--------|----------|---------------------------------|
| `report_id` | `str`  | Yes      | The unique ID of the report to delete. |

---

## Response

### Success Response

**Status Code:** `200 OK`  
**Response Body:**
```json
{
    "status": "success",
    "message": "Report deleted successfully",
    "data": {}
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
DELETE /api/v1/reports/report_1
```

### Example Response:
```json
{
    "status": "success",
    "message": "Report deleted successfully",
    "data": {}
}
```