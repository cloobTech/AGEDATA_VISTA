## RegressionInput Schema

### Description

The `RegressionInput` schema is used to define the input parameters for performing regression analysis. It specifies the type of regression, the feature columns, and the target column.

---

### Fields

| Field Name        | Type   | Default Value | Required | Description                                                                      |
| ----------------- | ------ | ------------- | -------- | -------------------------------------------------------------------------------- |
| `regression_type` | `str`  | `"linear"`    | No       | The type of regression to perform (e.g., `linear`, `decision_tree`, `logistic`). |
| `features_col`    | `list` |               | Yes      | A list of column names to use as features (independent variables).               |
| `label_col`       | `str`  |               | Yes      | The column name to use as the target (dependent variable).                       |

---

### Example Usage

#### Example Request Body

```json
{
  "regression_type": "linear",
  "features_col": ["educationlevel", "salary"],
  "label_col": "age"
}
```

---

### Full Request Body

```json
{
  "columns": ["educationlevel", "salary", "age"],
  "analysis_type": "regression",
  "generate_visualizations": true,
  "title": "Regression Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "regression_type": "linear",
    "features_col": ["educationlevel", "salary"],
    "label_col": "age"
  }
}
```

`NOTE: visualization is automatic, all you need to is set "{generate_visualizations": true}"`
