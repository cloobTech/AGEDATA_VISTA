# GradientBoostingInput Schema

**Description:**  
The `GradientBoostingInput` schema is used for performing gradient boosting modeling, including XGBoost and LightGBM. It allows users to specify the feature columns, target column, model type, and configuration for the selected gradient boosting model.

---

## Fields

### GradientBoostingType Enum

| Value      | Description              |
|------------|--------------------------|
| `xgboost`  | Use the XGBoost model.   |
| `lightgbm` | Use the LightGBM model.  |

---

### GradientBoostingConfig Schema

| Field Name          | Type        | Default Value | Required | Description                                                                 |
|---------------------|-------------|---------------|----------|-----------------------------------------------------------------------------|
| `n_estimators`      | `int`       | `100`         | No       | The number of boosting rounds (trees).                                     |
| `learning_rate`     | `float`     | `0.1`         | No       | The learning rate for boosting.                                            |
| `max_depth`         | `int`       | `3`           | No       | The maximum depth of the trees.                                            |
| `subsample`         | `float`     | `1.0`         | No       | The fraction of samples to use for training each tree (between 0 and 1).   |
| `random_state`      | `int`       | `None`        | No       | Controls the randomness of the estimator.                                  |
| `gamma`             | `float`     | `0`           | No       | Minimum loss reduction required to make a split (only for XGBoost).        |
| `reg_alpha`         | `float`     | `0`           | No       | L1 regularization term (only for XGBoost).                                 |
| `reg_lambda`        | `float`     | `1`           | No       | L2 regularization term (only for XGBoost).                                 |
| `num_leaves`        | `int`       | `31`          | No       | Maximum number of leaves in a tree (only for LightGBM).                    |
| `min_child_samples` | `int`       | `20`          | No       | Minimum number of data points in a leaf (only for LightGBM).               |

---

### GradientBoostingInput Schema

| Field Name    | Type        | Default Value | Required | Description                                                                 |
|---------------|-------------|---------------|----------|-----------------------------------------------------------------------------|
| `feature_cols`| `list[str]` |               | Yes      | A list of column names to use as features for the gradient boosting model.  |
| `target_col`  | `str`       |               | Yes      | The column name to use as the target variable.                              |
| `model_type`  | `GradientBoostingType` |   | Yes      | The type of gradient boosting model to use (`"xgboost"` or `"lightgbm"`).   |
| `config`      | `GradientBoostingConfig` | | Yes      | The configuration for the selected gradient boosting model.                 |
| `test_size`   | `float`     | `0.2`         | No       | The fraction of the dataset to use as the test set (between 0.1 and 0.5).   |
| `task_type`   | `str`       | `"classification"` | Yes  | The type of task (`"classification"` or `"regression"`).                    |

---

## Example Usage

### Example Request Body for XGBoost

```json
{
  "feature_cols": ["age", "salary", "experience"],
  "target_col": "department",
  "model_type": "xgboost",
  "config": {
    "n_estimators": 150,
    "learning_rate": 0.05,
    "max_depth": 6,
    "subsample": 0.8,
    "random_state": 42,
    "gamma": 0.1,
    "reg_alpha": 0.5,
    "reg_lambda": 1.0
  },
  "test_size": 0.2,
  "task_type": "classification"
}
```

---

### Example Request Body for LightGBM

```json
{
  "feature_cols": ["age", "salary", "experience"],
  "target_col": "department",
  "model_type": "lightgbm",
  "config": {
    "n_estimators": 200,
    "learning_rate": 0.1,
    "max_depth": 8,
    "subsample": 0.9,
    "random_state": 42,
    "num_leaves": 31,
    "min_child_samples": 10
  },
  "test_size": 0.3,
  "task_type": "regression"
}
```

---

### Full Request Body Example

```json
{
  "columns": ["age", "salary", "experience", "department"],
  "analysis_type": "gradient_boosting",
  "analysis_group": "advance",
  "generate_visualizations": true,
  "title": "Gradient Boosting Analysis Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "feature_cols": ["age", "salary", "experience"],
    "target_col": "department",
    "model_type": "xgboost",
    "config": {
      "n_estimators": 150,
      "learning_rate": 0.05,
      "max_depth": 6,
      "subsample": 0.8,
      "random_state": 42,
      "gamma": 0.1,
      "reg_alpha": 0.5,
      "reg_lambda": 1.0
    },
    "test_size": 0.2,
    "task_type": "classification"
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create gradient boosting visualizations.`