### TimeSeriesInput Schema

**Description:**  
The `TimeSeriesInput` schema is used for performing time series decomposition on a dataset. It allows users to specify the time and value columns, the decomposition model, and which components (observed, trend, seasonal, residual) to include in the output.

---

## Fields

| Field Name       | Type        | Default Value   | Required | Description                                                                 |
| ----------------- | ----------- | --------------- | -------- | --------------------------------------------------------------------------- |
| `time_col`       | `str`       |                 | Yes      | The column containing timestamps.                                           |
| `value_col`      | `str`       |                 | Yes      | The column containing values to analyze.                                    |
| `period`         | `int`       |                 | Yes      | specifies the number of time steps that make up a single seasonal cycle in the data.                                     |
| `freq`           | `str`       | `None`          | No       | The frequency string (e.g., `D` for daily, `M` for monthly).                |
| `model`          | `str`       | `"additive"`    | No       | The decomposition model to use (`additive` or `multiplicative`).            |
| `show_observed`  | `bool`      | `True`          | No       | Whether to include the observed component in the output.                    |
| `show_trend`     | `bool`      | `True`          | No       | Whether to include the trend component in the output.                       |
| `show_seasonal`  | `bool`      | `True`          | No       | Whether to include the seasonal component in the output.                    |
| `show_resid`     | `bool`      | `True`          | No       | Whether to include the residual component in the output.                    |

---

## Example Usage

### Example Request Body

```json
{
  "time_col": "date",
  "value_col": "sales",
  "freq": "D",
  "model": "multiplicative",
  "show_observed": true,
  "show_trend": true,
  "show_seasonal": true,
  "show_resid": true
}
```

---

### Full Request Body Example

```json
{
  "columns": ["date", "sales"],
  "analysis_type": "time_series_decomposition",
  "analysis_group": "time_series",
  "generate_visualizations": true,
  "title": "Time Series Decomposition Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "time_col": "date",
    "value_col": "sales",
    "freq": "D",
    "model": "multiplicative",
    "show_observed": true,
    "show_trend": true,
    "show_seasonal": true,
    "show_resid": true
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create time series decomposition visualizations.`