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

### Response
```json
{
	"status": "success",
	"message": "analysis performed successfully",
	"data": {
		"project_id": "35ff1cb1-12a1-4be7-a200-3c333165e6fb",
		"visualizations": {
			"confusion_matrix": "{\"data\":[{\"colorscale\":[[0.0,\"rgb(247,251,255)\"],[0.125,\"rgb(222,235,247)\"],[0.25,\"rgb(198,219,239)\"],[0.375,\"rgb(158,202,225)\"],[0.5,\"rgb(107,174,214)\"],[0.625,\"rgb(66,146,198)\"],[0.75,\"rgb(33,113,181)\"],[0.875,\"rgb(8,81,156)\"],[1.0,\"rgb(8,48,107)\"]],\"text\":{\"dtype\":\"i1\",\"bdata\":\"AwAAAAQHAAAG\",\"shape\":\"3, 3\"},\"texttemplate\":\"%{text}\",\"x\":[\"Class 0\",\"Class 1\",\"Class 2\"],\"y\":[\"Class 0\",\"Class 1\",\"Class 2\"],\"z\":{\"dtype\":\"i1\",\"bdata\":\"AwAAAAQHAAAG\",\"shape\":\"3, 3\"},\"type\":\"heatmap\"}],\"layout\":{\"template\":{\"data\":{\"histogram2dcontour\":[{\"type\":\"histogram2dcontour\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"choropleth\":[{\"type\":\"choropleth\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"histogram2d\":[{\"type\":\"histogram2d\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"heatmap\":[{\"type\":\"heatmap\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"contourcarpet\":[{\"type\":\"contourcarpet\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"contour\":[{\"type\":\"contour\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"surface\":[{\"type\":\"surface\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"mesh3d\":[{\"type\":\"mesh3d\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"scatter\":[{\"fillpattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2},\"type\":\"scatter\"}],\"parcoords\":[{\"type\":\"parcoords\",\"line\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterpolargl\":[{\"type\":\"scatterpolargl\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"bar\":[{\"error_x\":{\"color\":\"#2a3f5f\"},\"error_y\":{\"color\":\"#2a3f5f\"},\"marker\":{\"line\":{\"color\":\"#E5ECF6\",\"width\":0.5},\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"bar\"}],\"scattergeo\":[{\"type\":\"scattergeo\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterpolar\":[{\"type\":\"scatterpolar\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"histogram\":[{\"marker\":{\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"histogram\"}],\"scattergl\":[{\"type\":\"scattergl\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatter3d\":[{\"type\":\"scatter3d\",\"line\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}},\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattermap\":[{\"type\":\"scattermap\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattermapbox\":[{\"type\":\"scattermapbox\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterternary\":[{\"type\":\"scatterternary\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattercarpet\":[{\"type\":\"scattercarpet\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"carpet\":[{\"aaxis\":{\"endlinecolor\":\"#2a3f5f\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"minorgridcolor\":\"white\",\"startlinecolor\":\"#2a3f5f\"},\"baxis\":{\"endlinecolor\":\"#2a3f5f\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"minorgridcolor\":\"white\",\"startlinecolor\":\"#2a3f5f\"},\"type\":\"carpet\"}],\"table\":[{\"cells\":{\"fill\":{\"color\":\"#EBF0F8\"},\"line\":{\"color\":\"white\"}},\"header\":{\"fill\":{\"color\":\"#C8D4E3\"},\"line\":{\"color\":\"white\"}},\"type\":\"table\"}],\"barpolar\":[{\"marker\":{\"line\":{\"color\":\"#E5ECF6\",\"width\":0.5},\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"barpolar\"}],\"pie\":[{\"automargin\":true,\"type\":\"pie\"}]},\"layout\":{\"autotypenumbers\":\"strict\",\"colorway\":[\"#636efa\",\"#EF553B\",\"#00cc96\",\"#ab63fa\",\"#FFA15A\",\"#19d3f3\",\"#FF6692\",\"#B6E880\",\"#FF97FF\",\"#FECB52\"],\"font\":{\"color\":\"#2a3f5f\"},\"hovermode\":\"closest\",\"hoverlabel\":{\"align\":\"left\"},\"paper_bgcolor\":\"white\",\"plot_bgcolor\":\"#E5ECF6\",\"polar\":{\"bgcolor\":\"#E5ECF6\",\"angularaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"radialaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"}},\"ternary\":{\"bgcolor\":\"#E5ECF6\",\"aaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"baxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"caxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"}},\"coloraxis\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}},\"colorscale\":{\"sequential\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]],\"sequentialminus\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]],\"diverging\":[[0,\"#8e0152\"],[0.1,\"#c51b7d\"],[0.2,\"#de77ae\"],[0.3,\"#f1b6da\"],[0.4,\"#fde0ef\"],[0.5,\"#f7f7f7\"],[0.6,\"#e6f5d0\"],[0.7,\"#b8e186\"],[0.8,\"#7fbc41\"],[0.9,\"#4d9221\"],[1,\"#276419\"]]},\"xaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\",\"title\":{\"standoff\":15},\"zerolinecolor\":\"white\",\"automargin\":true,\"zerolinewidth\":2},\"yaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\",\"title\":{\"standoff\":15},\"zerolinecolor\":\"white\",\"automargin\":true,\"zerolinewidth\":2},\"scene\":{\"xaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2},\"yaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2},\"zaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2}},\"shapedefaults\":{\"line\":{\"color\":\"#2a3f5f\"}},\"annotationdefaults\":{\"arrowcolor\":\"#2a3f5f\",\"arrowhead\":0,\"arrowwidth\":1},\"geo\":{\"bgcolor\":\"white\",\"landcolor\":\"#E5ECF6\",\"subunitcolor\":\"white\",\"showland\":true,\"showlakes\":true,\"lakecolor\":\"white\"},\"title\":{\"x\":0.05},\"mapbox\":{\"style\":\"light\"}}},\"title\":{\"text\":\"Confusion Matrix\"},\"xaxis\":{\"title\":{\"text\":\"Predicted Label\"}},\"yaxis\":{\"title\":{\"text\":\"True Label\"}}}}",
			"metrics_plot": "{\"data\":[{\"marker\":{\"color\":[\"blue\",\"green\",\"orange\"]},\"x\":[\"accuracy\",\"precision_micro\",\"precision_macro\",\"precision_weighted\",\"recall_micro\",\"recall_macro\",\"recall_weighted\"],\"y\":[0.65,0.65,0.8205128205128206,0.8384615384615385,0.65,0.787878787878788,0.65],\"type\":\"bar\"}],\"layout\":{\"template\":{\"data\":{\"histogram2dcontour\":[{\"type\":\"histogram2dcontour\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"choropleth\":[{\"type\":\"choropleth\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"histogram2d\":[{\"type\":\"histogram2d\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"heatmap\":[{\"type\":\"heatmap\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"contourcarpet\":[{\"type\":\"contourcarpet\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"contour\":[{\"type\":\"contour\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"surface\":[{\"type\":\"surface\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"mesh3d\":[{\"type\":\"mesh3d\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"scatter\":[{\"fillpattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2},\"type\":\"scatter\"}],\"parcoords\":[{\"type\":\"parcoords\",\"line\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterpolargl\":[{\"type\":\"scatterpolargl\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"bar\":[{\"error_x\":{\"color\":\"#2a3f5f\"},\"error_y\":{\"color\":\"#2a3f5f\"},\"marker\":{\"line\":{\"color\":\"#E5ECF6\",\"width\":0.5},\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"bar\"}],\"scattergeo\":[{\"type\":\"scattergeo\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterpolar\":[{\"type\":\"scatterpolar\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"histogram\":[{\"marker\":{\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"histogram\"}],\"scattergl\":[{\"type\":\"scattergl\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatter3d\":[{\"type\":\"scatter3d\",\"line\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}},\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattermap\":[{\"type\":\"scattermap\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattermapbox\":[{\"type\":\"scattermapbox\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterternary\":[{\"type\":\"scatterternary\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattercarpet\":[{\"type\":\"scattercarpet\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"carpet\":[{\"aaxis\":{\"endlinecolor\":\"#2a3f5f\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"minorgridcolor\":\"white\",\"startlinecolor\":\"#2a3f5f\"},\"baxis\":{\"endlinecolor\":\"#2a3f5f\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"minorgridcolor\":\"white\",\"startlinecolor\":\"#2a3f5f\"},\"type\":\"carpet\"}],\"table\":[{\"cells\":{\"fill\":{\"color\":\"#EBF0F8\"},\"line\":{\"color\":\"white\"}},\"header\":{\"fill\":{\"color\":\"#C8D4E3\"},\"line\":{\"color\":\"white\"}},\"type\":\"table\"}],\"barpolar\":[{\"marker\":{\"line\":{\"color\":\"#E5ECF6\",\"width\":0.5},\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"barpolar\"}],\"pie\":[{\"automargin\":true,\"type\":\"pie\"}]},\"layout\":{\"autotypenumbers\":\"strict\",\"colorway\":[\"#636efa\",\"#EF553B\",\"#00cc96\",\"#ab63fa\",\"#FFA15A\",\"#19d3f3\",\"#FF6692\",\"#B6E880\",\"#FF97FF\",\"#FECB52\"],\"font\":{\"color\":\"#2a3f5f\"},\"hovermode\":\"closest\",\"hoverlabel\":{\"align\":\"left\"},\"paper_bgcolor\":\"white\",\"plot_bgcolor\":\"#E5ECF6\",\"polar\":{\"bgcolor\":\"#E5ECF6\",\"angularaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"radialaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"}},\"ternary\":{\"bgcolor\":\"#E5ECF6\",\"aaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"baxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"caxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"}},\"coloraxis\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}},\"colorscale\":{\"sequential\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]],\"sequentialminus\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]],\"diverging\":[[0,\"#8e0152\"],[0.1,\"#c51b7d\"],[0.2,\"#de77ae\"],[0.3,\"#f1b6da\"],[0.4,\"#fde0ef\"],[0.5,\"#f7f7f7\"],[0.6,\"#e6f5d0\"],[0.7,\"#b8e186\"],[0.8,\"#7fbc41\"],[0.9,\"#4d9221\"],[1,\"#276419\"]]},\"xaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\",\"title\":{\"standoff\":15},\"zerolinecolor\":\"white\",\"automargin\":true,\"zerolinewidth\":2},\"yaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\",\"title\":{\"standoff\":15},\"zerolinecolor\":\"white\",\"automargin\":true,\"zerolinewidth\":2},\"scene\":{\"xaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2},\"yaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2},\"zaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2}},\"shapedefaults\":{\"line\":{\"color\":\"#2a3f5f\"}},\"annotationdefaults\":{\"arrowcolor\":\"#2a3f5f\",\"arrowhead\":0,\"arrowwidth\":1},\"geo\":{\"bgcolor\":\"white\",\"landcolor\":\"#E5ECF6\",\"subunitcolor\":\"white\",\"showland\":true,\"showlakes\":true,\"lakecolor\":\"white\"},\"title\":{\"x\":0.05},\"mapbox\":{\"style\":\"light\"}}},\"yaxis\":{\"title\":{\"text\":\"Score\"},\"range\":[0,1]},\"title\":{\"text\":\"Model Performance Metrics\"}}}"
		},
		"summary": {
			"metrics": {
				"accuracy": 0.65,
				"precision_micro": 0.65,
				"precision_macro": 0.8205128205128206,
				"precision_weighted": 0.8384615384615385,
				"recall_micro": 0.65,
				"recall_macro": 0.787878787878788,
				"recall_weighted": 0.65
			},
			"model_params": {
				"kernel": "rbf",
				"support_vectors": [
					[
						92.0,
						44000.0,
						24.0
					],
					[
						82.0,
						46000.0,
						25.0
					],
					[
						41.0,
						38000.0,
						23.0
					],
					[
						2.0,
						40000.0,
						23.0
					],
					[
						42.0,
						44000.0,
						25.0
					],
					[
						22.0,
						41000.0,
						25.0
					],
					[
						81.0,
						40000.0,
						23.0
					],
					[
						12.0,
						45000.0,
						26.0
					],
					[
						11.0,
						42000.0,
						24.0
					],
					[
						91.0,
						39000.0,
						22.0
					],
					[
						72.0,
						43000.0,
						24.0
					],
					[
						71.0,
						38000.0,
						22.0
					],
					[
						52.0,
						42000.0,
						24.0
					],
					[
						21.0,
						37000.0,
						23.0
					],
					[
						62.0,
						45000.0,
						25.0
					],
					[
						39.0,
						97000.0,
						41.0
					],
					[
						10.0,
						100000.0,
						42.0
					],
					[
						59.0,
						99000.0,
						41.0
					],
					[
						84.0,
						65000.0,
						29.0
					],
					[
						64.0,
						64000.0,
						29.0
					],
					[
						43.0,
						56000.0,
						28.0
					],
					[
						19.0,
						98000.0,
						43.0
					],
					[
						73.0,
						56000.0,
						26.0
					],
					[
						79.0,
						101000.0,
						41.0
					],
					[
						50.0,
						103000.0,
						44.0
					],
					[
						69.0,
						100000.0,
						42.0
					],
					[
						80.0,
						106000.0,
						43.0
					],
					[
						90.0,
						107000.0,
						44.0
					],
					[
						3.0,
						50000.0,
						25.0
					],
					[
						33.0,
						54000.0,
						26.0
					],
					[
						30.0,
						101000.0,
						44.0
					],
					[
						83.0,
						58000.0,
						27.0
					],
					[
						54.0,
						62000.0,
						28.0
					],
					[
						4.0,
						60000.0,
						28.0
					],
					[
						93.0,
						57000.0,
						26.0
					],
					[
						89.0,
						102000.0,
						42.0
					],
					[
						49.0,
						98000.0,
						42.0
					],
					[
						13.0,
						62000.0,
						29.0
					],
					[
						23.0,
						52000.0,
						27.0
					],
					[
						44.0,
						63000.0,
						30.0
					],
					[
						40.0,
						102000.0,
						43.0
					],
					[
						74.0,
						63000.0,
						28.0
					],
					[
						94.0,
						64000.0,
						28.0
					],
					[
						70.0,
						105000.0,
						44.0
					],
					[
						15.0,
						78000.0,
						33.0
					],
					[
						38.0,
						92000.0,
						39.0
					],
					[
						16.0,
						83000.0,
						36.0
					],
					[
						85.0,
						82000.0,
						32.0
					],
					[
						45.0,
						78000.0,
						32.0
					],
					[
						96.0,
						88000.0,
						33.0
					],
					[
						65.0,
						80000.0,
						32.0
					],
					[
						97.0,
						93000.0,
						36.0
					],
					[
						7.0,
						85000.0,
						35.0
					],
					[
						86.0,
						87000.0,
						34.0
					],
					[
						36.0,
						82000.0,
						33.0
					],
					[
						76.0,
						86000.0,
						33.0
					],
					[
						25.0,
						76000.0,
						32.0
					],
					[
						77.0,
						91000.0,
						36.0
					],
					[
						5.0,
						75000.0,
						30.0
					],
					[
						46.0,
						83000.0,
						35.0
					],
					[
						87.0,
						92000.0,
						37.0
					],
					[
						75.0,
						81000.0,
						31.0
					],
					[
						67.0,
						90000.0,
						37.0
					],
					[
						26.0,
						81000.0,
						34.0
					],
					[
						57.0,
						89000.0,
						36.0
					],
					[
						28.0,
						91000.0,
						40.0
					],
					[
						47.0,
						88000.0,
						37.0
					],
					[
						48.0,
						93000.0,
						40.0
					],
					[
						56.0,
						84000.0,
						33.0
					],
					[
						55.0,
						79000.0,
						31.0
					],
					[
						95.0,
						83000.0,
						31.0
					],
					[
						35.0,
						77000.0,
						31.0
					],
					[
						27.0,
						86000.0,
						37.0
					]
				],
				"n_support": [
					15,
					29,
					29
				]
			}
		},
		"title": "SVM",
		"analysis_group": "advance",
		"ai_report": "**Model Performance Summary**\n\nThe model's performance can be summarized as follows:\n\n* **Accuracy**: 65%\n* **Precision**: \n  + Micro average: 65%\n  + Macro average: 82.05%\n  + Weighted average: 83.85%\n* **Recall**: \n  + Micro average: 65%\n  + Macro average: 78.79%\n  + Weighted average: 65%\n\n**Model Parameters**\n\n* **Kernel**: rbf (Radial Basis Function)\n* **Support Vectors**: 30 data points are used as support vectors by the model.\n\n**Support Vector Distribution**\n\nThe support vectors are distributed across three classes:\n\n* Class 1: 15 support vectors\n* Class 2: 29 support vectors\n* Class 3: 29 support vectors\n\nThese support vectors are likely to be the most informative data points for the model's decision boundary. \n\nNo further analysis can be provided without more context on the dataset and the specific problem being addressed. \n\nHow can I assist you further?",
		"id": "1881aa88-c08e-497c-b618-f879273c57b4",
		"created_at": "2025-05-28T12:37:24.988149Z",
		"updated_at": "2025-05-28T12:37:24.988222Z",
		"_class_": "Report"
	}
}
```