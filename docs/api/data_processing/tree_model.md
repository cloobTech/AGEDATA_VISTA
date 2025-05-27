# TreeModelInput Schema

**Description:**  
The `TreeModelInput` schema is used for performing tree-based modeling, including Decision Trees and Random Forests. It allows users to specify the feature columns, target column, model type, and configuration for the selected tree-based model.

---

## Fields

### TreeModelType Enum

| Value            | Description                     |
|------------------|---------------------------------|
| `decision_tree`  | Use a Decision Tree model.      |
| `random_forest`  | Use a Random Forest model.      |

---

### TreeModelConfig Schema

| Field Name          | Type        | Default Value | Required | Description                                                                 |
|---------------------|-------------|---------------|----------|-----------------------------------------------------------------------------|
| `max_depth`         | `int`       | `None`        | No       | The maximum depth of the tree. If `None`, nodes are expanded until all leaves are pure or contain fewer than `min_samples_split` samples. |
| `min_samples_split` | `int`       | `2`           | No       | The minimum number of samples required to split an internal node.           |
| `min_samples_leaf`  | `int`       | `1`           | No       | The minimum number of samples required to be at a leaf node.                |
| `criterion`         | `str`       | `"gini"`      | No       | The function to measure the quality of a split (`"gini"`, `"entropy"`, or `"log_loss"`). |
| `random_state`      | `int`       | `None`        | No       | Controls the randomness of the estimator.                                   |
| `n_estimators`      | `int`       | `100`         | No       | The number of trees in the forest (only applicable for Random Forest).      |
| `max_features`      | `str`       | `"sqrt"`      | No       | The number of features to consider when looking for the best split (only applicable for Random Forest). |

---

### TreeModelInput Schema

| Field Name    | Type        | Default Value | Required | Description                                                                 |
|---------------|-------------|---------------|----------|-----------------------------------------------------------------------------|
| `feature_cols`| `list[str]` |               | Yes      | A list of column names to use as features for the tree-based model.         |
| `target_col`  | `str`       |               | Yes      | The column name to use as the target variable.                              |
| `model_type`  | `TreeModelType` |           | Yes      | The type of tree-based model to use (`"decision_tree"` or `"random_forest"`). |
| `config`      | `TreeModelConfig` |         | Yes      | The configuration for the selected tree-based model.                        |
| `test_size`   | `float`     | `0.2`         | No       | The fraction of the dataset to use as the test set (between 0.1 and 0.5).   |
| `task_type`   | `str`       |               | Yes      | The type of task (`"classification"` or `"regression"`).                    |

---

## Example Usage

### Example Request Body for Decision Tree

```json
{
  "feature_cols": ["age", "salary", "experience"],
  "target_col": "department",
  "model_type": "decision_tree",
  "config": {
    "max_depth": 5,
    "min_samples_split": 2,
    "min_samples_leaf": 1,
    "criterion": "gini",
    "random_state": 42
  },
  "test_size": 0.2,
  "task_type": "classification"
}
```

---

### Example Request Body for Random Forest

```json
{
  "feature_cols": ["age", "salary", "experience"],
  "target_col": "department",
  "model_type": "random_forest",
  "config": {
    "max_depth": 10,
    "min_samples_split": 3,
    "min_samples_leaf": 2,
    "criterion": "entropy",
    "random_state": 42,
    "n_estimators": 150,
    "max_features": "sqrt"
  },
  "test_size": 0.3,
  "task_type": "classification"
}
```

---

### Full Request Body Example

```json
{
  "columns": ["age", "salary", "experience", "department"],
  "analysis_type": "tree_model",
  "analysis_group": "advance",
  "generate_visualizations": true,
  "title": "Tree Model Analysis Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "feature_cols": ["age", "salary", "experience"],
    "target_col": "department",
    "model_type": "random_forest",
    "config": {
      "max_depth": 10,
      "min_samples_split": 3,
      "min_samples_leaf": 2,
      "criterion": "entropy",
      "random_state": 42,
      "n_estimators": 150,
      "max_features": "sqrt"
    },
    "test_size": 0.3,
    "task_type": "classification"
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create tree model visualizations.`