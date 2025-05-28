# SVMInput Schema

**Description:**  
The `SVMInput` schema is used for performing Support Vector Machine (SVM) modeling. It allows users to specify the feature columns, target column, and configuration for the SVM model, including kernel type, regularization, and other hyperparameters.

---

## Fields

### SVMKernel Enum

| Value      | Description                          |
|------------|--------------------------------------|
| `linear`   | Use a linear kernel.                 |
| `poly`     | Use a polynomial kernel.             |
| `rbf`      | Use a radial basis function (RBF) kernel. |
| `sigmoid`  | Use a sigmoid kernel.                |

---

### SVMConfig Schema

| Field Name      | Type        | Default Value | Required | Description                                                                 |
|-----------------|-------------|---------------|----------|-----------------------------------------------------------------------------|
| `C`            | `float`     | `1.0`         | No       | Regularization parameter. Higher values reduce regularization.             |
| `kernel`       | `SVMKernel` | `"rbf"`       | No       | The kernel type to use (`"linear"`, `"poly"`, `"rbf"`, `"sigmoid"`).        |
| `degree`       | `int`       | `3`           | No       | Degree for polynomial kernel (only applicable for `"poly"` kernel).         |
| `gamma`        | `str`       | `"scale"`     | No       | Kernel coefficient (`"scale"` or `"auto"`).                                 |
| `probability`  | `bool`      | `True`        | No       | Whether to enable probability estimates.                                    |
| `random_state` | `int`       | `None`        | No       | Controls the randomness of the estimator.                                  |

---

### SVMInput Schema

| Field Name    | Type        | Default Value | Required | Description                                                                 |
|---------------|-------------|---------------|----------|-----------------------------------------------------------------------------|
| `feature_cols`| `list[str]` |               | Yes      | A list of column names to use as features for the SVM model.                |
| `target_col`  | `str`       |               | Yes      | The column name to use as the target variable.                              |
| `test_size`   | `float`     | `0.2`         | No       | The fraction of the dataset to use as the test set (between 0.1 and 0.5).   |
| `config`      | `SVMConfig` |               | Yes      | The configuration for the SVM model.                                       |
| `task_type`   | `str`       |               | Yes      | The type of task (`"classification"` or `"regression"`).                    |

---

## Example Usage

### Example Request Body for Classification

```json
{
  "feature_cols": ["age", "salary", "experience"],
  "target_col": "department",
  "test_size": 0.2,
  "config": {
    "C": 1.0,
    "kernel": "rbf",
    "degree": 3,
    "gamma": "scale",
    "probability": true,
    "random_state": 42
  },
  "task_type": "classification"
}
```

---

### Example Request Body for Regression

```json
{
  "feature_cols": ["age", "salary", "experience"],
  "target_col": "salary",
  "test_size": 0.3,
  "config": {
    "C": 0.5,
    "kernel": "linear",
    "degree": 3,
    "gamma": "auto",
    "probability": false,
    "random_state": 42
  },
  "task_type": "regression"
}
```

---

### Full Request Body Example

```json
{
  "columns": ["age", "salary", "experience", "department"],
  "analysis_type": "svm",
  "analysis_group": "advance",
  "generate_visualizations": true,
  "title": "SVM Analysis Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "feature_cols": ["age", "salary", "experience"],
    "target_col": "department",
    "test_size": 0.2,
    "config": {
      "C": 1.0,
      "kernel": "rbf",
      "degree": 3,
      "gamma": "scale",
      "probability": true,
      "random_state": 42
    },
    "task_type": "classification"
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create SVM visualizations.`