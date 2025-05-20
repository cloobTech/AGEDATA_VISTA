# Forecasting Configuration Schemas

This document provides details and examples for the configuration schemas used in forecasting models: **SARIMAX**, **Prophet**, and **ARIMA**.

---

## SARIMAXConfig Schema

**Description:**  
The `SARIMAXConfig` schema is used to configure the SARIMAX model, which supports seasonal and non-seasonal ARIMA models with optional exogenous variables.

### Fields

| Field Name              | Type        | Default Value | Required | Description                       |
| ----------------------- | ----------- | ------------- | -------- | --------------------------------- |
| `order`                 | `list[int]` |               | Yes      | ARIMA order: `[p, d, q]`.         |
| `seasonal_order`        | `list[int]` | `None`        | No       | Seasonal order: `[P, D, Q, s]`.   |
| `enforce_stationarity`  | `bool`      | `True`        | No       | Whether to enforce stationarity.  |
| `enforce_invertibility` | `bool`      | `True`        | No       | Whether to enforce invertibility. |

### Example Usage

```json
{
  "model_type": "sarimax",
  "time_col": "date",
  "value_col": "sales",
  "forecast_steps": 5,
  "test_size": 0.2,
  "sarimax": {
    "order": [1, 1, 1],
    "seasonal_order": [1, 1, 0, 12],
    "enforce_stationarity": true,
    "enforce_invertibility": true
  }
}
```

---

## ProphetConfig Schema

**Description:**  
The `ProphetConfig` schema is used to configure the Prophet model, which supports additive or multiplicative seasonality and flexible trend changes.

### Fields

| Field Name                | Type         | Default Value | Required | Description                                           |
| ------------------------- | ------------ | ------------- | -------- | ----------------------------------------------------- |
| `seasonality_mode`        | `str`        | `"additive"`  | No       | Seasonality mode: `"additive"` or `"multiplicative"`. |
| `yearly_seasonality`      | `bool`       | `True`        | No       | Whether to include yearly seasonality.                |
| `weekly_seasonality`      | `bool`       | `False`       | No       | Whether to include weekly seasonality.                |
| `daily_seasonality`       | `bool`       | `False`       | No       | Whether to include daily seasonality.                 |
| `changepoint_prior_scale` | `float`      | `0.05`        | No       | Controls flexibility of trend changes.                |
| `holidays`                | `list[dict]` | `None`        | No       | List of holiday definitions.                          |

### Example Usage

```json
{
  "model_type": "prophet",
  "time_col": "date",
  "value_col": "sales",
  "forecast_steps": 5,
  "test_size": 0.2,
  "prophet": {
    "seasonality_mode": "additive",
    "yearly_seasonality": true,
    "weekly_seasonality": true,
    "daily_seasonality": false,
    "changepoint_prior_scale": 0.1,
    "holidays": [
      {
        "holiday": "New Year",
        "ds": "2023-01-01",
        "lower_window": 0,
        "upper_window": 1
      },
      {
        "holiday": "Christmas",
        "ds": "2023-12-25",
        "lower_window": -1,
        "upper_window": 0
      }
    ]
  }
}
```

---

## ARIMAConfig Schema

**Description:**  
The `ARIMAConfig` schema is used to configure the ARIMA model, which supports non-seasonal ARIMA models.

### Fields

| Field Name | Type        | Default Value | Required | Description               |
| ---------- | ----------- | ------------- | -------- | ------------------------- |
| `order`    | `list[int]` |               | Yes      | ARIMA order: `[p, d, q]`. |

### Example Usage

```json
{
  "model_type": "arima",
  "time_col": "date",
  "value_col": "sales",
  "forecast_steps": 5,
  "test_size": 0.2,
  "arima": {
    "order": [1, 1, 1]
  }
}
```

---

## ForecastInput Schema

**Description:**  
The `ForecastInput` schema is the main input schema for forecasting. It allows users to specify the time column, value column, model type, and configuration for the selected model.

### Fields

| Field Name       | Type            | Default Value | Required | Description                                                |
| ---------------- | --------------- | ------------- | -------- | ---------------------------------------------------------- |
| `time_col`       | `str`           |               | Yes      | The column containing time series data.                    |
| `value_col`      | `str`           |               | Yes      | The column containing the target variable.                 |
| `exog_cols`      | `list[str]`     | `None`        | No       | List of exogenous variable columns (optional).             |
| `forecast_steps` | `int`           | `10`          | Yes      | Number of steps to forecast into the future.               |
| `model_type`     | `str`           |               | Yes      | The type of model: `"sarimax"`, `"prophet"`, or `"arima"`. |
| `sarimax`        | `SARIMAXConfig` | `None`        | No       | Configuration for SARIMAX model.                           |
| `prophet`        | `ProphetConfig` | `None`        | No       | Configuration for Prophet model.                           |
| `arima`          | `ARIMAConfig`   | `None`        | No       | Configuration for ARIMA model.                             |
| `test_size`      | `float`         | `None`        | No       | Fraction of data to use as the test set.                   |

---

### Full Example Request Body

`EXAMPLE WITH SARIMAX`

```json
{
  "columns": ["date", "sales"],
  "analysis_type": "forecast",
  "analysis_group": "time_series",
  "generate_visualizations": true,
  "title": "Forecasting Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "time_col": "date",
    "value_col": "sales",
    "forecast_steps": 5,
    "model_type": "sarimax",
    "sarimax": {
      "order": [1, 1, 1],
      "seasonal_order": [1, 1, 0, 12],
      "enforce_stationarity": true,
      "enforce_invertibility": true
    }
  }
}
```

`EXAMPLE WITH PROPHET`

```json
{
  "columns": ["date", "sales"],
  "analysis_group": "time_series",
  "analysis_type": "forecast",
  "generate_visualizations": true,
  "title": "Holt-Winters Forecasting (ARIMA)",
  "file_id": "f1f1bfb0-de98-472f-9bb1-af1d37326098",
  "project_id": "d16694b3-629d-481f-9274-e1993479a3a1",
  "analysis_input": {
    "time_col": "date",
    "value_col": "sales",
    "forecast_steps": 5,
    "model_type": "prophet",
    "prophet": {
      "seasonality_mode": "additive",
      "yearly_seasonality": true,
      "weekly_seasonality": true,
      "daily_seasonality": false,
      "changepoint_prior_scale": 0.05
    },
    "test_size": 0.2
  }
}
```

`EXAMPLE WITH ARIMA`

```json
{
  "columns": ["date", "sales"],
  "analysis_group": "time_series",
  "analysis_type": "forecast",
  "generate_visualizations": true,
  "title": "Holt-Winters Forecasting (ARIMA)",
  "file_id": "f1f1bfb0-de98-472f-9bb1-af1d37326098",
  "project_id": "d16694b3-629d-481f-9274-e1993479a3a1",
  "analysis_input": {
    "time_col": "date",
    "value_col": "sales",
    "forecast_steps": 20,
    "model_type": "arima",
    "arima": {
      "order": [1, 1, 1]
    },
    "test_size": 0.2
  }
}
```
