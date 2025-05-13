### MovingAverageInput Schema

**Description:**  
The `MovingAverageInput` schema is used for performing moving average calculations on a dataset. It allows users to specify the time and value columns, the window size, and additional options such as centering and the type of moving average.

---

## Fields

| Field Name    | Type        | Default Value   | Required | Description                                                                 |
| ------------- | ----------- | --------------- | -------- | --------------------------------------------------------------------------- |
| `time_col`    | `str`       |                 | Yes      | The column containing timestamps or sequence numbers.                       |
| `value_col`   | `str`       |                 | Yes      | The column containing values to analyze.                                    |
| `window_size` | `int`       |                 | Yes      | The size of the moving window.                                              |
| `min_periods` | `int`       | `None`          | No       | The minimum number of observations in the window required to compute a value. |
| `center`      | `bool`      | `False`         | No       | Whether to center the moving average.                                       |
| `ma_type`     | `str`       | `"simple"`      | No       | The type of moving average to compute (`simple`, `cumulative`, `weighted`, `exponential`). |

---

## Example Usage

### Example Request Body

```json
{
  "time_col": "date",
  "value_col": "sales",
  "window_size": 7,
  "min_periods": 3,
  "center": true,
  "ma_type": "simple"
}
```

---

### Full Request Body Example

```json
{
  "columns": ["date", "sales"],
  "analysis_type": "moving_average",
  "analysis_group": "time_series",
  "generate_visualizations": true,
  "title": "Moving Average Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "time_col": "date",
    "value_col": "sales",
    "window_size": 7,
    "min_periods": 3,
    "center": true,
    "ma_type": "simple"
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create moving average visualizations.`