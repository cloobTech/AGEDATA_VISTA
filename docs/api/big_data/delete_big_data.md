### 3. **Delete Big Data Report**

#### Endpoint

`DELETE /api/v1/analysis/big-data/{report_id}`

#### Description

Delete a big data report by its `report_id`.

#### Request

##### URL Parameters

| Name        | Type   | Required | Description                  |
| ----------- | ------ | -------- | ---------------------------- |
| `report_id` | string | Yes      | The unique ID of the report. |

##### Headers

| Name            | Type   | Required | Description                           |
| --------------- | ------ | -------- | ------------------------------------- |
| `Authorization` | string | Yes      | Bearer token for user authentication. |

#### Response

##### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object confirming the deletion.

```json
{
  "status": "success",
  "message": "Big data report deleted successfully",
  "data": {
    "report_id": "70f422e1-c593-4062-a7f4-e9a33ac927a3"
  }
}
```

##### Error Response

- **Status Code:** `404 Not Found`

  - **Detail:** Report not found.
  - **Example:**
    ```json
    {
      "detail": "Report not found"
    }
    ```

- **Status Code:** `500 Internal Server Error`
  - **Detail:** Failed to delete the report.
  - **Example:**
    ```json
    {
      "detail": "Failed to delete report: <error_message>"
    }
    ```

---

### Notes

- Use the `task_id` or `report_id` returned from the **Start Big Data Analysis** endpoint to retrieve, update, or delete reports.
- Ensure proper authentication headers are included in the request.
