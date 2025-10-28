## Big Data Analysis Endpoints

### 1. **Start Big Data Analysis**

#### Endpoint

`POST /api/v1/analysis/big-data`

#### Description

This endpoint starts a big data analysis task using PySpark and Celery. The task runs asynchronously, and a unique `task_id` is returned to track the progress of the analysis.

#### Request

##### Headers

| Name            | Type   | Required | Description                           |
| --------------- | ------ | -------- | ------------------------------------- |
| `Authorization` | string | Yes      | Bearer token for user authentication. |
| `Content-Type`  | string | Yes      | Must be `application/json`.           |

##### JSON Body Parameters

| Name                        | Type    | Required | Description                                                          |
| --------------------------- | ------- | -------- | -------------------------------------------------------------------- |
| `source_config`             | object  | Yes      | Configuration for the data source.                                   |
| `source_config.type`        | string  | Yes      | Type of the data source (`file`, `database` etc.)|
| `source_config.path`        | string  | No       | Path to the file (if `type` is `file`).                              |
| `source_config.url`         | string  | No       | URL of the file (if `type` is `url`).                                |
| `source_config.format`      | string  | No       | Format of the file (`csv`, `parquet`, `excel`, `json`, `auto` etc.). |
| `numeric_columns`           | list    | No       | List of numeric columns to analyze.                                  |
| `time_column`               | string  | No       | Column containing timestamps.                                        |
| `value_column`              | string  | No       | Column containing values to analyze.                                 |
| `group_columns`             | list    | No       | List of columns to group data by.                                    |
| `perform_anomaly_detection` | boolean | No       | Whether to perform anomaly detection.                                |
| `anomaly_method`            | string  | No       | Method for anomaly detection (`iqr` or `zscore`).                    |
| `period`                    | integer | No       | Period for time series analysis.                                     |
| `model`                     | string  | No       | Model type (`additive` or `multiplicative`).                         |

##### Example Request Body

```json
{
  "source_config": {
    "type": "file",
    "path": "/path/to/data.parquet",
    "format": "parquet"
  },
  "numeric_columns": ["sales", "revenue", "quantity"],
  "time_column": "date",
  "value_column": "sales",
  "perform_anomaly_detection": true,
  "anomaly_method": "iqr",
  "period": 12,
  "model": "additive"
}
```

#### Response

##### Success Response

- **Status Code:** `202 Accepted`
- **Body:** A JSON object containing the `task_id` to track the progress of the analysis.

```json
{
  "status": "success",
  "message": "Big data analysis started successfully",
  "data": {
    "task_id": "70f422e1-c593-4062-a7f4-e9a33ac927a3"
  }
}
```

##### Error Response

- **Status Code:** `500 Internal Server Error`
  - **Detail:** Failed to start the analysis.
  - **Example:**
    ```json
    {
      "detail": "Failed to start analysis: <error_message>"
    }
    ```

---

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

---

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
