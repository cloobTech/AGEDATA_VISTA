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
| `source_config.type`        | string  | Yes      | Type of the data source (`file`, `database` etc.)                    |
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
    "type": "url",
    "url": "https://raw.githubusercontent.com/datasets/covid-19/main/data/countries-aggregated.csv",
    "format": "csv"
  },
  "analyses": ["data_profile", "statistical_analysis", "time_series_analysis"],
  "time_column": "Date",
  "value_columns": ["Confirmed", "Recovered", "Deaths"],
  "filters": [{ "column": "Country", "value": "Afghanistan" }],
  "generate_visualizations": true,
  "title": "Big Data Analysis",
  "user_id": "8810df9b-e755-42c6-ac8b-31414b52b203"
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

## Configuration Sources for Big Data Analysis

### 1. **File Source Configuration**

| Key      | Type   | Required | Description                                      |
| -------- | ------ | -------- | ------------------------------------------------ |
| `type`   | string | Yes      | The type of the source. Must be `file`.          |
| `path`   | string | Yes      | The file path to the data.                       |
| `format` | string | Yes      | The format of the file (`csv`, `parquet`, etc.). |

#### Example

```json
{
  "type": "file",
  "path": "/data/sales.parquet",
  "format": "parquet"
}
```

---

### 2. **URL Source Configuration**

| Key      | Type   | Required | Description                                   |
| -------- | ------ | -------- | --------------------------------------------- |
| `type`   | string | Yes      | The type of the source. Must be `url`.        |
| `url`    | string | Yes      | The URL to the data file.                     |
| `format` | string | Yes      | The format of the file (`csv`, `json`, etc.). |

#### Example

```json
{
  "type": "url",
  "url": "https://example.com/data.csv",
  "format": "csv"
}
```

---

### 3. **Database Source Configuration**

| Key        | Type   | Required | Description                                 |
| ---------- | ------ | -------- | ------------------------------------------- |
| `type`     | string | Yes      | The type of the source. Must be `database`. |
| `url`      | string | Yes      | The JDBC URL for the database connection.   |
| `table`    | string | Yes      | The name of the table to query.             |
| `username` | string | Yes      | The username for database authentication.   |
| `password` | string | Yes      | The password for database authentication.   |

#### Example

```json
{
  "type": "database",
  "url": "jdbc:postgresql://localhost:5432/mydb",
  "table": "sales_data",
  "username": "user",
  "password": "pass"
}
```

---

### 4. **Cloud Storage Source Configuration**

| Key        | Type   | Required | Description                              |
| ---------- | ------ | -------- | ---------------------------------------- |
| `type`     | string | Yes      | The type of the source. Must be `cloud`. |
| `path`     | string | Yes      | The cloud storage path to the data.      |
| `provider` | string | Yes      | The cloud provider (`s3`, `gcs`, etc.).  |

#### Example

```json
{
  "type": "cloud",
  "path": "s3://bucket/data.parquet",
  "provider": "s3"
}
```

---

### Notes

- **File Source**: Use this configuration for local files or files accessible on the server.
- **URL Source**: Use this configuration for files hosted on a public or private URL.
- **Database Source**: Use this configuration for querying data directly from a database.
- **Cloud Storage Source**: Use this configuration for files stored in cloud storage services like AWS S3 or Google Cloud Storage.

---

## Big Data Analysis Input Schema

### Description

The `BigDataAnalysisInput` schema defines the structure of the input required to start a big data analysis task. It supports various configurations for data sources, analysis options, and additional features like anomaly detection and visualization generation.

---

### Schema Fields

| Field                       | Type            | Required                        | Default                                                                      | Description |
| --------------------------- | --------------- | ------------------------------- | ---------------------------------------------------------------------------- | ----------- |
| `title`                     | string          | No `"Big Data Analysis Report"` | The title of the analysis report.                                            |
| `value_columns`             | list of strings | No `None`                       | List of columns containing values to analyze.                                |
| `source_config`             | object          | Yes -                           | Configuration for the data source (e.g., file, URL, database, cloud).        |
| `numeric_columns`           | list of strings | No `None`                       | List of numeric columns to analyze.                                          |
| `time_column`               | string          | No `None`                       | The column containing timestamps.                                            |
| `value_column`              | string          | No `None`                       | The column containing values to analyze.                                     |
| `group_columns`             | list of strings | No `None`                       | List of columns to group data by.                                            |
| `perform_anomaly_detection` | boolean         | No `False`                      | Whether to perform anomaly detection.                                        |
| `anomaly_method`            | string          | No `"iqr"`                      | Method for anomaly detection (`iqr` or `zscore`).                            |
| `filters`                   | list of objects | No `None`                       | Filters to apply to the dataset (e.g., filter by column value).              |
| `generate_visualizations`   | boolean         | No `True`                       | Whether to generate visualizations for the analysis.                         |
| `analyses`                  | list of strings | No `None`                       | Types of analyses to perform (e.g., `data_profile`, `time_series_analysis`,`statistical_analysis`, `anomaly_detection`, `pattern_analysis`, `data_drift_analysis`)|
| `period`                    | integer         | No `None`                       | Period for time series analysis (1-365).                                     |
| `model`                     | string          | No `"additive"`                 | Model type for time series analysis (`additive` or `multiplicative`).        |

---

### Field Details

#### `source_config`

The `source_config` field defines the data source configuration. It supports the following types:

- **File Source**: Local files or files accessible on the server.
- **URL Source**: Files hosted on a public or private URL.
- **Database Source**: Data queried directly from a database.
- **Cloud Storage Source**: Files stored in cloud storage services like AWS S3 or Google Cloud Storage.

---

### Example Input Configurations

#### 1. **COVID-19 Data Analysis**

```json
{
  "title": "COVID-19 Country Analysis",
  "source_config": {
    "type": "url",
    "url": "https://raw.githubusercontent.com/datasets/covid-19/main/data/countries-aggregated.csv",
    "format": "csv"
  },
  "analyses": ["data_profile", "time_series_analysis"],
  "time_column": "Date",
  "value_columns": ["Confirmed", "Recovered", "Deaths"],
  "filters": [{ "column": "Country", "value": "Afghanistan" }],
  "generate_visualizations": true
}
```

#### 2. **Sales Data Analysis**

```json
{
  "title": "Quarterly Sales Report",
  "source_config": {
    "type": "file",
    "path": "/data/sales_q4.parquet",
    "format": "parquet"
  },
  "numeric_columns": ["amount", "quantity", "profit"],
  "time_column": "order_date",
  "value_column": "amount",
  "group_columns": ["region", "product_category"],
  "perform_anomaly_detection": true,
  "anomaly_method": "zscore"
}
```

#### 3. **Database Analysis**

```json
{
  "title": "Customer Analytics",
  "source_config": {
    "type": "database",
    "url": "jdbc:postgresql://localhost:5432/analytics",
    "table": "customer_behavior",
    "username": "analyst",
    "password": "secure_password"
  },
  "numeric_columns": ["session_duration", "page_views", "purchase_amount"],
  "group_columns": ["age_group", "country"]
}
```


### Complete Request Structure
```json
{
    "source_config": {
        "type": "url",
        "url": "https://example.com/data.csv",
        "format": "csv"
    },
    "analyses": [
        "data_profile",
        "statistical_analysis", 
        "time_series_analysis",
        "anomaly_detection",
        "pattern_analysis"
    ],
    "time_column": "date",
    "value_columns": ["sales", "revenue"],
    "value_column": "sales",  // Alternative single column
    "numeric_columns": ["sales", "revenue", "quantity"],
    "group_columns": ["region", "category"],
    "filters": [
        {"column": "year", "operator": ">", "value": 2020}
    ],
    "perform_anomaly_detection": true,
    "anomaly_method": "iqr",
    "period": 7,
    "model": "additive",
    "generate_visualizations": true,
    "aggregation_method": "mean"
}
```

---

### Notes

- **Filters**: The `filters` field allows you to specify conditions to filter the dataset. For example:
  ```json
  "filters": [{"column": "Country", "value": "Afghanistan"}]
  ```
- **Analyses**: The `analyses` field specifies the types of analyses to perform. Examples include:
  - `data_profile`: Generate a data profile summary.
  - `time_series_analysis`: Perform time series analysis.
  - `statistical_analysis`: Perform statistical analysis.
- **Anomaly Detection**: If `perform_anomaly_detection` is set to `true`, you can specify the `anomaly_method` as either `iqr` (Interquartile Range) or `zscore`.

This schema provides flexibility for various data analysis use cases, including time series analysis, anomaly detection, and data profiling.
