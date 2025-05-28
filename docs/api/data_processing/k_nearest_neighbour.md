# KNNInput Schema

**Description:**  
The `KNNInput` schema is used for performing K-Nearest Neighbors (KNN) modeling. It allows users to specify the feature columns, target column, and configuration for the KNN model, including the number of neighbors, distance metric, and algorithm.

---

## Fields

### KNNWeights Enum

| Value      | Description                          |
|------------|--------------------------------------|
| `uniform`  | All points in each neighborhood are weighted equally. |
| `distance` | Points are weighted by the inverse of their distance. |

---

### KNNAlgorithm Enum

| Value        | Description                          |
|--------------|--------------------------------------|
| `auto`       | Automatically chooses the best algorithm based on the dataset. |
| `ball_tree`  | Uses Ball Tree algorithm.            |
| `kd_tree`    | Uses KD Tree algorithm.              |
| `brute`      | Uses brute-force search.             |

---

### KNNConfig Schema

| Field Name      | Type        | Default Value | Required | Description                                                                 |
|-----------------|-------------|---------------|----------|-----------------------------------------------------------------------------|
| `n_neighbors`   | `int`       | `5`           | No       | The number of neighbors to use for classification or regression.           |
| `weights`       | `KNNWeights`| `"uniform"`   | No       | Weight function used in prediction (`"uniform"` or `"distance"`).           |
| `algorithm`     | `KNNAlgorithm` | `"auto"`   | No       | Algorithm used to compute the nearest neighbors (`"auto"`, `"ball_tree"`, `"kd_tree"`, `"brute"`). |
| `p`             | `int`       | `2`           | No       | Power parameter for Minkowski distance.                                     |
| `metric`        | `str`       | `"minkowski"` | No       | Distance metric to use.                                                     |

---

### KNNInput Schema

| Field Name    | Type        | Default Value | Required | Description                                                                 |
|---------------|-------------|---------------|----------|-----------------------------------------------------------------------------|
| `feature_cols`| `list[str]` |               | Yes      | A list of column names to use as features for the KNN model.                |
| `target_col`  | `str`       |               | Yes      | The column name to use as the target variable.                              |
| `test_size`   | `float`     | `0.2`         | No       | The fraction of the dataset to use as the test set (between 0.1 and 0.5).   |
| `config`      | `KNNConfig` |               | Yes      | The configuration for the KNN model.                                       |
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
    "n_neighbors": 5,
    "weights": "uniform",
    "algorithm": "auto",
    "p": 2,
    "metric": "minkowski"
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
    "n_neighbors": 10,
    "weights": "distance",
    "algorithm": "kd_tree",
    "p": 1,
    "metric": "minkowski"
  },
  "task_type": "regression"
}
```

---

### Full Request Body Example

```json
{
  "columns": ["age", "salary", "experience", "department"],
  "analysis_type": "knn",
  "analysis_group": "advance",
  "generate_visualizations": true,
  "title": "KNN Analysis Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "feature_cols": ["age", "salary", "experience"],
    "target_col": "department",
    "test_size": 0.2,
    "config": {
      "n_neighbors": 5,
      "weights": "uniform",
      "algorithm": "auto",
      "p": 2,
      "metric": "minkowski"
    },
    "task_type": "classification"
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create KNN visualizations.`