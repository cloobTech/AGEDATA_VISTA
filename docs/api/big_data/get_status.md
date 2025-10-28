### 2. **Get Big Data Analysis Status**

#### Endpoint

`GET /api/v1/analysis/big-data/{task_id}/status`

#### Description

This endpoint retrieves the current status of a big data analysis task.

#### Request

##### URL Parameters

| Name      | Type   | Required | Description                         |
| --------- | ------ | -------- | ----------------------------------- |
| `task_id` | string | Yes      | The unique ID of the analysis task. |

##### Headers

| Name            | Type   | Required | Description                           |
| --------------- | ------ | -------- | ------------------------------------- |
| `Authorization` | string | Yes      | Bearer token for user authentication. |

#### Response

##### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the current status of the task.

```json
{
  "status": "success",
  "message": "Analysis status retrieved successfully",
  "data": {
    "status": "RUNNING",
    "progress": 50,
    "message": "",
    "task_id": "70f422e1-c593-4062-a7f4-e9a33ac927a3"
  }
}
```

##### Error Response

- **Status Code:** `500 Internal Server Error`
  - **Detail:** Failed to retrieve the task status.
  - **Example:**
    ```json
    {
      "detail": "Failed to get task status: <error_message>"
    }
    ```


### Notes

- Use the `task_id` returned from the **Start Big Data Analysis** endpoint to track the progress of the task.
- The **Stream Big Data Analysis Progress** endpoint provides real-time updates, while the **Get Big Data Analysis Status** endpoint provides a one-time snapshot of the task's progress.