### ExponentialSmoothingInput Schema

**Description:**  
The `ExponentialSmoothingInput` schema is used for performing exponential smoothing on a dataset. It allows users to specify the time and value columns, smoothing parameters, and options for trend and seasonality.

---

## Fields

| Field Name         | Type        | Default Value   | Required | Description                                                                 |
| ------------------- | ----------- | --------------- | -------- | --------------------------------------------------------------------------- |
| `time_col`         | `str`       |                 | Yes      | The column containing timestamps or sequence numbers.                       |
| `value_col`        | `str`       |                 | Yes      | The column containing values to analyze.                                    |
| `smoothing_level`  | `float`     | `None`          | No       | The alpha parameter for smoothing.                                          |
| `trend`            | `str`       | `None`          | No       | The type of trend component (`add` or `mul`).                               |
| `seasonal`         | `str`       | `None`          | No       | The type of seasonal component (`add` or `mul`).                            |
| `seasonal_periods` | `int`       | `None`          | No       | The number of periods in a seasonal cycle.                                  |
| `damped_trend`     | `bool`      | `False`         | No       | Whether to use a damped trend.                                              |

---

## Example Usage

### Example Request Body

```json
{
  "time_col": "date",
  "value_col": "sales",
  "smoothing_level": 0.2,
  "trend": "add",
  "seasonal": "mul",
  "seasonal_periods": 12,
  "damped_trend": true
}
```

---

### Full Request Body Example

```json
{
  "columns": ["date", "sales"],
  "analysis_type": "exponential_smoothing",
  "analysis_group": "time_series",
  "generate_visualizations": true,
  "title": "Exponential Smoothing Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "time_col": "date",
    "value_col": "sales",
    "smoothing_level": 0.2,
    "trend": "add",
    "seasonal": "mul",
    "seasonal_periods": 12,
    "damped_trend": true
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create exponential smoothing visualizations.`