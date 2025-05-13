### ACFPACFInput Schema

**Description:**  
The `Autocorrelation (ACF) and Partial Autocorrelation (PACF) ` schema is used for performing Autocorrelation Function (ACF) and Partial Autocorrelation Function (PACF) analysis on a dataset. It allows users to specify the time and value columns, the number of lags, and additional options such as confidence level and computation methods.

---

## Fields

| Field Name    | Type        | Default Value   | Required | Description                                                                 |
| ------------- | ----------- | --------------- | -------- | --------------------------------------------------------------------------- |
| `time_col`    | `str`       |                 | Yes      | The column containing timestamps or sequence numbers.                       |
| `value_col`   | `str`       |                 | Yes      | The column containing values to analyze.                                    |
| `nlags`       | `int`       | `40`            | No       | The number of lags to compute.                                              |
| `alpha`       | `float`     | `0.05`          | No       | The confidence level for significance bounds.                               |
| `fft`         | `bool`      | `True`          | No       | Whether to use FFT for ACF computation.                                     |
| `method`      | `str`       | `"yw"`          | No       | The method to use for PACF computation (`'yw'`, `'ols'`, `'ld'`).           |

---

## Example Usage

### Example Request Body

```json
{
  "time_col": "date",
  "value_col": "sales",
  "nlags": 30,
  "alpha": 0.05,
  "fft": true,
  "method": "ols"
}
```

---

### Full Request Body Example

```json
{
  "columns": ["date", "sales"],
  "analysis_type": "acf_pacf",
  "analysis_group": "time_series",
  "generate_visualizations": true,
  "title": "ACF and PACF Analysis Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "time_col": "date",
    "value_col": "sales",
    "nlags": 30,
    "alpha": 0.05,
    "fft": true,
    "method": "ols"
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create ACF and PACF visualizations.`