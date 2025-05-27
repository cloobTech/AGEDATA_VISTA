# LogisticRegressionInput Schema

**Description:**  
The `LogisticRegressionInput` schema is used for performing logistic regression analysis. It allows users to specify the feature columns, target column, test size, and various hyperparameters for the logistic regression model.

---

## Fields

| Field Name    | Type        | Default Value | Required | Description                                                                 |
|---------------|-------------|---------------|----------|-----------------------------------------------------------------------------|
| `feature_cols`| `list[str]` |               | Yes      | A list of column names to use as features for the logistic regression model.|
| `target_col`  | `str`       |               | Yes      | The column name to use as the target variable.                              |
| `test_size`   | `float`     | `0.2`         | No       | The fraction of the dataset to use as the test set (between 0.1 and 0.5).   |
| `penalty`     | `str`       | `"l2"`        | No       | The regularization penalty to use (`"l2"` or `"none"`).                     |
| `solver`      | `str`       | `"lbfgs"`     | No       | The solver to use for optimization (`"lbfgs"`, `"liblinear"`, `"sag"`, `"saga"`, `"newton-cg"`). |
| `max_iter`    | `int`       | `100`         | No       | The maximum number of iterations for the solver.                           |
| `multi_class` | `str`       | `"ovr"`       | No       | The multi-class strategy to use (`"ovr"` for one-vs-rest, `"ovo"` for one-vs-one). |

---

## Example Usage

### Example Request Body

```json
{
  "feature_cols": ["age", "salary", "experience"],
  "target_col": "department",
  "test_size": 0.2,
  "penalty": "l2",
  "solver": "lbfgs",
  "max_iter": 200,
  "multi_class": "ovr"
}
```

---

### Full Request Body Example

```json
{
  "columns": ["age", "salary", "experience", "department"],
  "analysis_type": "logistic_regression",
  "analysis_group": "advance",
  "generate_visualizations": true,
  "title": "Logistic Regression Analysis Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "feature_cols": ["age", "salary", "experience"],
    "target_col": "department",
    "test_size": 0.2,
    "penalty": "l2",
    "solver": "lbfgs",
    "max_iter": 200,
    "multi_class": "ovr"
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create logistic regression visualizations.`