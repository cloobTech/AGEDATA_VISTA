### 3. **Stream Big Data Analysis Progress**

#### Endpoint

`GET /api/v1/analysis/stream-progress/{task_id}`

#### Description

This endpoint streams the progress of a big data analysis task via **Server-Sent Events (SSE)**. It provides real-time updates on the task's progress.

#### Request

##### URL Parameters

| Name      | Type   | Required | Description                         |
| --------- | ------ | -------- | ----------------------------------- |
| `task_id` | string | Yes      | The unique ID of the analysis task. |

##### Headers

| Name     | Type   | Required | Description                  |
| -------- | ------ | -------- | ---------------------------- |
| `Accept` | string | Yes      | Must be `text/event-stream`. |

#### Response

The response is streamed as **Server-Sent Events (SSE)** with the following fields:

##### Event Data Format

```json
{
  "task_id": "70f422e1-c593-4062-a7f4-e9a33ac927a3",
  "progress": 80,
  "status": "RUNNING",
  "message": "",
  "data": {
    "status": "PROCESSING",
    "progress": 80
  }
}
```

##### Example Event Data

```json
{
  "task_id": "70f422e1-c593-4062-a7f4-e9a33ac927a3",
  "progress": 80,
  "status": "RUNNING",
  "message": "",
  "data": {
    "status": "PROCESSING",
    "progress": 80
  }
}
```

##### Error Response

- **Status Code:** `500 Internal Server Error`
  - **Detail:** Failed to stream the task progress.
  - **Example:**
    ```json
    {
      "detail": "Failed to stream task progress: <error_message>"
    }
    ```

---

### Notes

- Use the `task_id` returned from the **Start Big Data Analysis** endpoint to track the progress of the task.
- The **Stream Big Data Analysis Progress** endpoint provides real-time updates, while the **Get Big Data Analysis Status** endpoint provides a one-time snapshot of the task's progress.