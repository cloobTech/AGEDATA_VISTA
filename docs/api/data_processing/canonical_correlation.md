### CCAInput Schema

**Description:**  
The `CCAInput` schema is used for performing Canonical Correlation Analysis (CCA) on a dataset. It allows users to specify the sets of variables (X and Y), the number of components to retain, and whether to scale the data.

---

## Fields

| Field Name    | Type        | Default Value | Required | Description                                                                 |
| ------------- | ----------- | ------------- | -------- | --------------------------------------------------------------------------- |
| `x_cols`      | `list[str]` |               | Yes      | A list of column names to use as the X variables in the analysis.           |
| `y_cols`      | `list[str]` |               | Yes      | A list of column names to use as the Y variables in the analysis.           |
| `n_components`| `int`       | `2`           | No       | The number of canonical components to retain.                               |
| `scale_data`  | `bool`      | `True`        | No       | Whether to scale the data before performing the analysis (recommended).     |

---

## Example Usage

### Example Request Body

```json
{
  "x_cols": ["age", "salary", "experience"],
  "y_cols": ["department_score", "performance_rating"],
  "n_components": 3,
  "scale_data": true
}
```

---

### Full Request Body Example

```json
{
  "columns": ["age", "salary", "experience", "department_score", "performance_rating"],
  "analysis_type": "canonical_correlation",
  "analysis_group": "multi_variate",
  "generate_visualizations": true,
  "title": "CCA Analysis Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "x_cols": ["age", "salary", "experience"],
    "y_cols": ["department_score", "performance_rating"],
    "n_components": 3,
    "scale_data": true
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create CCA visualizations.`