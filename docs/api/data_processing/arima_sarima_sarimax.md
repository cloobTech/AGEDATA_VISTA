### ARIMA/SARIMA/SARIMAX Schema

**Description:**  
The `ARIMA/SARIMA/SARIMAX` schema is used for performing ARIMA, SARIMA, or SARIMAX analysis on a dataset. These models are used for time series forecasting and allow users to specify the time and value columns, model parameters, and additional options for stationarity and invertibility.

- **ARIMA**: AutoRegressive Integrated Moving Average  
- **SARIMA**: Seasonal AutoRegressive Integrated Moving Average  
- **SARIMAX**: Seasonal AutoRegressive Integrated Moving Average with eXogenous variables  

---

## Fields

| Field Name            | Type            | Default Value   | Required | Description                                                                 |
| --------------------- | --------------- | --------------- | -------- | --------------------------------------------------------------------------- |
| `time_col`           | `str`           |                 | Yes      | The column containing timestamps.                                           |
| `value_col`          | `str`           |                 | Yes      | The column containing values to analyze.                                    |
| `exog_cols`          | `list[str]`     | `None`          | No       | A list of column names for exogenous variables (used in SARIMAX).           |
| `order`              | `list[int]`     |                 | Yes      | The ARIMA model order (`p`, `d`, `q`).                                      |
| `seasonal_order`     | `list[int]`     | `None`          | No       | The seasonal order for SARIMA/SARIMAX (`P`, `D`, `Q`, `s`).                 |
| `enforce_stationarity` | `bool`        | `True`          | No       | Whether to enforce stationarity in the model.                               |
| `enforce_invertibility`| `bool`        | `True`          | No       | Whether to enforce invertibility in the model.                              |

---

## Example Usage

### Example Request Body

```json
{
  "time_col": "date",
  "value_col": "sales",
  "exog_cols": ["promotion", "holiday"],
  "order": [1, 1, 1],
  "seasonal_order": [1, 1, 0, 12],
  "enforce_stationarity": true,
  "enforce_invertibility": true
}
```

---

### Full Request Body Example

```json
{
  "columns": ["date", "sales", "promotion", "holiday"],
  "analysis_type": "arima",
  "analysis_group": "time_series",
  "generate_visualizations": true,
  "title": "ARIMA Analysis Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "time_col": "date",
    "value_col": "sales",
    "exog_cols": ["promotion", "holiday"],
    "order": [1, 1, 1],
    "seasonal_order": [1, 1, 0, 12],
    "enforce_stationarity": true,
    "enforce_invertibility": true
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create ARIMA-related visualizations.`