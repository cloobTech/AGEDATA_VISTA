# NeuralNetworkInput Schema

**Description:**  
The `NeuralNetworkInput` schema is used for configuring and performing neural network modeling. It allows users to specify the feature columns, target column, and configuration for the neural network, including hidden layers, activation functions, optimization algorithms, and training parameters.

---

## Fields

### ActivationFunction Enum

| Value      | Description                          |
|------------|--------------------------------------|
| `relu`     | Rectified Linear Unit activation function. |
| `sigmoid`  | Sigmoid activation function.         |
| `tanh`     | Hyperbolic tangent activation function. |
| `softmax`  | Softmax activation function.         |

---

### OptimizerType Enum

| Value      | Description                          |
|------------|--------------------------------------|
| `adam`     | Adam optimization algorithm.         |
| `sgd`      | Stochastic Gradient Descent.         |
| `rmsprop`  | RMSprop optimization algorithm.      |

---

### NeuralNetworkConfig Schema

| Field Name        | Type        | Default Value | Required | Description                                                                 |
|-------------------|-------------|---------------|----------|-----------------------------------------------------------------------------|
| `hidden_layers`   | `list[int]` | `[64, 32]`    | No       | Number of neurons in each hidden layer.                                     |
| `activation`      | `ActivationFunction` | `"relu"` | No       | Activation function to use (`"relu"`, `"sigmoid"`, `"tanh"`, `"softmax"`).  |
| `optimizer`       | `OptimizerType` | `"adam"`   | No       | Optimization algorithm to use (`"adam"`, `"sgd"`, `"rmsprop"`).             |
| `learning_rate`   | `float`     | `0.001`       | No       | Learning rate for the optimizer.                                            |
| `epochs`          | `int`       | `50`          | No       | Number of training epochs.                                                  |
| `batch_size`      | `int`       | `32`          | No       | Batch size for training.                                                    |
| `dropout_rate`    | `float`     | `None`        | No       | Dropout rate for regularization (between 0 and 0.5).                        |
| `early_stopping`  | `bool`      | `True`        | No       | Whether to enable early stopping during training.                           |
| `validation_split`| `float`     | `0.1`         | No       | Fraction of data to use for validation (between 0.05 and 0.3).              |

---

### NeuralNetworkInput Schema

| Field Name    | Type        | Default Value | Required | Description                                                                 |
|---------------|-------------|---------------|----------|-----------------------------------------------------------------------------|
| `feature_cols`| `list[str]` |               | Yes      | A list of column names to use as features for the neural network model.     |
| `target_col`  | `str`       |               | Yes      | The column name to use as the target variable.                              |
| `test_size`   | `float`     | `0.2`         | No       | The fraction of the dataset to use as the test set (between 0.1 and 0.5).   |
| `config`      | `NeuralNetworkConfig` |     | Yes      | The configuration for the neural network model.                            |
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
    "hidden_layers": [128, 64],
    "activation": "relu",
    "optimizer": "adam",
    "learning_rate": 0.001,
    "epochs": 100,
    "batch_size": 32,
    "dropout_rate": 0.2,
    "early_stopping": true,
    "validation_split": 0.1
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
    "hidden_layers": [64, 32],
    "activation": "tanh",
    "optimizer": "sgd",
    "learning_rate": 0.01,
    "epochs": 50,
    "batch_size": 16,
    "dropout_rate": null,
    "early_stopping": false,
    "validation_split": 0.2
  },
  "task_type": "regression"
}
```

---

### Full Request Body Example

```json
{
  "columns": ["age", "salary", "experience", "department"],
  "analysis_type": "neural_network",
  "analysis_group": "advance",
  "generate_visualizations": true,
  "title": "Neural Network Analysis Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "feature_cols": ["age", "salary", "experience"],
    "target_col": "department",
    "test_size": 0.2,
    "config": {
      "hidden_layers": [128, 64],
      "activation": "relu",
      "optimizer": "adam",
      "learning_rate": 0.001,
      "epochs": 100,
      "batch_size": 32,
      "dropout_rate": 0.2,
      "early_stopping": true,
      "validation_split": 0.1
    },
    "task_type": "classification"
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create neural network visualizations.`