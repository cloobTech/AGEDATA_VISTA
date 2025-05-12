### PCAInput Schema

**Description:**  
The `PCAInput` schema is used for performing Principal Component Analysis (PCA) on a dataset. It allows users to specify the numeric columns to include, the number of components to retain, and additional options such as scaling the data and grouping by color.

---

## Fields

| Field Name    | Type        | Default Value | Required | Description                                                                 |
| ------------- | ----------- | ------------- | -------- | --------------------------------------------------------------------------- |
| `numeric_cols`| `list[str]` |               | Yes      | A list of column names to use for PCA.                                      |
| `n_components`| `int`       | `None`        | No       | The number of principal components to retain. If `None`, all components are kept. |
| `scale_data`  | `bool`      | `True`        | No       | Whether to scale the data before performing PCA (recommended).              |
| `color_col`   | `str`       | `None`        | No       | An optional column name for grouping data points by color in visualizations.|
| `hover_col`   | `str`       | `None`        | No       | An optional column name for additional hover information in visualizations. |

---

## Example Usage

### Example Request Body

```json
{
  "numeric_cols": ["age", "salary", "experience"],
  "n_components": 2,
  "scale_data": true,
  "color_col": "department",
  "hover_col": "gender"
}
```

---

### Full Request Body Example

```json
{
  "columns": ["age", "salary", "experience"],
  "analysis_type": "pca",
  "analysis_group": "multi_variate",
  "generate_visualizations": true,
  "title": "PCA Analysis Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "numeric_cols": ["age", "salary", "experience"],
    "n_components": 2,
    "scale_data": true,
    "color_col": "department",
    "hover_col": "gender"
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create PCA visualizations.`