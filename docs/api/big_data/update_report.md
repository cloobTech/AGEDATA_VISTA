###  **Update Big Data Report**

#### Endpoint

`PUT /api/v1/analysis/big-data/{report_id}`

#### Description

Update a big data report by its `report_id`.

#### Request

##### URL Parameters

| Name        | Type   | Required | Description                     |
| ----------- | ------ | -------- | ------------------------------- |
| `report_id` | string | Yes      | The unique ID of the report.    |

##### Headers

| Name            | Type   | Required | Description                           |
| --------------- | ------ | -------- | ------------------------------------- |
| `Authorization` | string | Yes      | Bearer token for user authentication. |

##### JSON Body Parameters

| Name         | Type   | Required | Description                     |
| ------------ | ------ | -------- | ------------------------------- |
| `update_data`| object | Yes      | The data to update in the report.|

##### Example Request Body

```json
{
    "update_data": {
        "name": "Updated Report Name",
        "description": "Updated description for the report"
    }
}
```

#### Response

##### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object confirming the update.

```json
{
    "status": "success",
    "message": "Big data report updated successfully",
    "data": {
        "report_id": "70f422e1-c593-4062-a7f4-e9a33ac927a3",
        "updated_fields": {
            "name": "Updated Report Name",
            "description": "Updated description for the report"
        }
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
  - **Detail:** Failed to update the report.
  - **Example:**
    ```json
    {
        "detail": "Failed to update report: <error_message>"
    }
    ```


