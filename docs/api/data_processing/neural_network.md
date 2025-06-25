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

### Response
```json
{
	"status": "success",
	"message": "analysis performed successfully",
	"data": {
		"project_id": "35ff1cb1-12a1-4be7-a200-3c333165e6fb",
		"visualizations": {
			"training_history": "{\"data\":[{\"line\":{\"color\":\"blue\"},\"name\":\"Training Loss\",\"x\":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75],\"y\":[1.1986206769943237,1.1379115581512451,1.0991671085357666,1.0828033685684204,1.0297389030456543,1.0172945261001587,0.977667510509491,0.9705393314361572,0.9467807412147522,0.9268286824226379,0.9299412965774536,0.9123108386993408,0.8985929489135742,0.8677346706390381,0.8691948652267456,0.8369317054748535,0.8349268436431885,0.8016750812530518,0.8039848804473877,0.8068035244941711,0.7650988101959229,0.7527444362640381,0.7289484739303589,0.7417687773704529,0.7094408273696899,0.6853314638137817,0.6966950297355652,0.6746106743812561,0.6762006282806396,0.68204665184021,0.67367023229599,0.6379176378250122,0.6633961200714111,0.6179332733154297,0.6379345655441284,0.5777118802070618,0.602716326713562,0.6133752465248108,0.5830734372138977,0.5834628939628601,0.5492045879364014,0.5935499668121338,0.5744313597679138,0.5100136995315552,0.5234670042991638,0.5566227436065674,0.5194269418716431,0.5628013014793396,0.5041529536247253,0.5291054844856262,0.4907626509666443,0.49032676219940186,0.5010846257209778,0.4919165074825287,0.461999773979187,0.45072290301322937,0.4331607520580292,0.47279125452041626,0.48562607169151306,0.44037649035453796,0.42605605721473694,0.4235471785068512,0.4087205231189728,0.41529810428619385,0.40328601002693176,0.42111605405807495,0.36432382464408875,0.4261551797389984,0.3727916479110718,0.4112490713596344,0.39480480551719666,0.37663930654525757,0.39195331931114197,0.3736293911933899,0.4104716181755066,0.37077581882476807],\"type\":\"scatter\",\"xaxis\":\"x\",\"yaxis\":\"y\"},{\"line\":{\"color\":\"red\"},\"name\":\"Validation Loss\",\"x\":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75],\"y\":[0.9902642965316772,0.9647104144096375,0.9441810250282288,0.9316501617431641,0.9196637868881226,0.90550696849823,0.8905528783798218,0.8705178499221802,0.8512826561927795,0.8332986831665039,0.8186007738113403,0.802775502204895,0.7849652171134949,0.7653931975364685,0.745060920715332,0.7256019115447998,0.7097965478897095,0.69903564453125,0.6904040575027466,0.6785635948181152,0.6684478521347046,0.6573137640953064,0.6489608287811279,0.644159197807312,0.6406556367874146,0.6370024681091309,0.6284332275390625,0.6199232339859009,0.6115233898162842,0.5979909896850586,0.583708643913269,0.5716970562934875,0.5645651817321777,0.5509103536605835,0.5302367806434631,0.5170921683311462,0.5020154714584351,0.49061983823776245,0.48543012142181396,0.4794272780418396,0.47103774547576904,0.46115559339523315,0.44608980417251587,0.43044281005859375,0.41550642251968384,0.4025036692619324,0.3899775445461273,0.38300609588623047,0.37867283821105957,0.376217246055603,0.37222811579704285,0.3711403012275696,0.37261539697647095,0.37338265776634216,0.3724220395088196,0.36801382899284363,0.3614649176597595,0.3559070825576782,0.35517439246177673,0.3544303774833679,0.3506089448928833,0.3431200385093689,0.33450770378112793,0.32764798402786255,0.3173714280128479,0.30918604135513306,0.3024452328681946,0.2971076965332031,0.2911452353000641,0.28645747900009155,0.28439027070999146,0.2898761034011841,0.2936609387397766,0.2940495014190674,0.2875829339027405,0.2864782214164734],\"type\":\"scatter\",\"xaxis\":\"x\",\"yaxis\":\"y\"},{\"line\":{\"color\":\"blue\"},\"name\":\"Training Accuracy\",\"showlegend\":false,\"x\":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75],\"y\":[0.1666666716337204,0.1527777761220932,0.2083333283662796,0.2638888955116272,0.3611111044883728,0.4583333432674408,0.5555555820465088,0.5,0.6527777910232544,0.6527777910232544,0.5833333134651184,0.625,0.625,0.7638888955116272,0.6805555820465088,0.6666666865348816,0.75,0.7916666865348816,0.6944444179534912,0.6388888955116272,0.7361111044883728,0.8055555820465088,0.7777777910232544,0.7222222089767456,0.7777777910232544,0.8055555820465088,0.7916666865348816,0.8055555820465088,0.7083333134651184,0.6666666865348816,0.7916666865348816,0.75,0.7361111044883728,0.8055555820465088,0.7916666865348816,0.8472222089767456,0.8055555820465088,0.7222222089767456,0.7361111044883728,0.8055555820465088,0.8333333134651184,0.75,0.8055555820465088,0.875,0.7777777910232544,0.8055555820465088,0.8333333134651184,0.75,0.7222222089767456,0.75,0.8194444179534912,0.8333333134651184,0.7916666865348816,0.8055555820465088,0.8333333134651184,0.8333333134651184,0.875,0.8333333134651184,0.8055555820465088,0.8055555820465088,0.8472222089767456,0.8333333134651184,0.875,0.8611111044883728,0.8194444179534912,0.8472222089767456,0.8888888955116272,0.7916666865348816,0.8888888955116272,0.8472222089767456,0.8333333134651184,0.875,0.8611111044883728,0.8611111044883728,0.875,0.875],\"type\":\"scatter\",\"xaxis\":\"x2\",\"yaxis\":\"y2\"},{\"line\":{\"color\":\"red\"},\"name\":\"Validation Accuracy\",\"showlegend\":false,\"x\":[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75],\"y\":[0.5,0.5,0.625,0.5,0.375,0.375,0.375,0.5,0.5,0.625,0.625,0.75,0.875,0.875,0.875,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0],\"type\":\"scatter\",\"xaxis\":\"x2\",\"yaxis\":\"y2\"}],\"layout\":{\"template\":{\"data\":{\"histogram2dcontour\":[{\"type\":\"histogram2dcontour\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"choropleth\":[{\"type\":\"choropleth\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"histogram2d\":[{\"type\":\"histogram2d\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"heatmap\":[{\"type\":\"heatmap\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"contourcarpet\":[{\"type\":\"contourcarpet\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"contour\":[{\"type\":\"contour\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"surface\":[{\"type\":\"surface\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"mesh3d\":[{\"type\":\"mesh3d\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"scatter\":[{\"fillpattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2},\"type\":\"scatter\"}],\"parcoords\":[{\"type\":\"parcoords\",\"line\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterpolargl\":[{\"type\":\"scatterpolargl\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"bar\":[{\"error_x\":{\"color\":\"#2a3f5f\"},\"error_y\":{\"color\":\"#2a3f5f\"},\"marker\":{\"line\":{\"color\":\"#E5ECF6\",\"width\":0.5},\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"bar\"}],\"scattergeo\":[{\"type\":\"scattergeo\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterpolar\":[{\"type\":\"scatterpolar\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"histogram\":[{\"marker\":{\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"histogram\"}],\"scattergl\":[{\"type\":\"scattergl\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatter3d\":[{\"type\":\"scatter3d\",\"line\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}},\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattermap\":[{\"type\":\"scattermap\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattermapbox\":[{\"type\":\"scattermapbox\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterternary\":[{\"type\":\"scatterternary\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattercarpet\":[{\"type\":\"scattercarpet\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"carpet\":[{\"aaxis\":{\"endlinecolor\":\"#2a3f5f\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"minorgridcolor\":\"white\",\"startlinecolor\":\"#2a3f5f\"},\"baxis\":{\"endlinecolor\":\"#2a3f5f\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"minorgridcolor\":\"white\",\"startlinecolor\":\"#2a3f5f\"},\"type\":\"carpet\"}],\"table\":[{\"cells\":{\"fill\":{\"color\":\"#EBF0F8\"},\"line\":{\"color\":\"white\"}},\"header\":{\"fill\":{\"color\":\"#C8D4E3\"},\"line\":{\"color\":\"white\"}},\"type\":\"table\"}],\"barpolar\":[{\"marker\":{\"line\":{\"color\":\"#E5ECF6\",\"width\":0.5},\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"barpolar\"}],\"pie\":[{\"automargin\":true,\"type\":\"pie\"}]},\"layout\":{\"autotypenumbers\":\"strict\",\"colorway\":[\"#636efa\",\"#EF553B\",\"#00cc96\",\"#ab63fa\",\"#FFA15A\",\"#19d3f3\",\"#FF6692\",\"#B6E880\",\"#FF97FF\",\"#FECB52\"],\"font\":{\"color\":\"#2a3f5f\"},\"hovermode\":\"closest\",\"hoverlabel\":{\"align\":\"left\"},\"paper_bgcolor\":\"white\",\"plot_bgcolor\":\"#E5ECF6\",\"polar\":{\"bgcolor\":\"#E5ECF6\",\"angularaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"radialaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"}},\"ternary\":{\"bgcolor\":\"#E5ECF6\",\"aaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"baxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"caxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"}},\"coloraxis\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}},\"colorscale\":{\"sequential\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]],\"sequentialminus\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]],\"diverging\":[[0,\"#8e0152\"],[0.1,\"#c51b7d\"],[0.2,\"#de77ae\"],[0.3,\"#f1b6da\"],[0.4,\"#fde0ef\"],[0.5,\"#f7f7f7\"],[0.6,\"#e6f5d0\"],[0.7,\"#b8e186\"],[0.8,\"#7fbc41\"],[0.9,\"#4d9221\"],[1,\"#276419\"]]},\"xaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\",\"title\":{\"standoff\":15},\"zerolinecolor\":\"white\",\"automargin\":true,\"zerolinewidth\":2},\"yaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\",\"title\":{\"standoff\":15},\"zerolinecolor\":\"white\",\"automargin\":true,\"zerolinewidth\":2},\"scene\":{\"xaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2},\"yaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2},\"zaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2}},\"shapedefaults\":{\"line\":{\"color\":\"#2a3f5f\"}},\"annotationdefaults\":{\"arrowcolor\":\"#2a3f5f\",\"arrowhead\":0,\"arrowwidth\":1},\"geo\":{\"bgcolor\":\"white\",\"landcolor\":\"#E5ECF6\",\"subunitcolor\":\"white\",\"showland\":true,\"showlakes\":true,\"lakecolor\":\"white\"},\"title\":{\"x\":0.05},\"mapbox\":{\"style\":\"light\"}}},\"xaxis\":{\"anchor\":\"y\",\"domain\":[0.0,0.45],\"title\":{\"text\":\"Epochs\"}},\"yaxis\":{\"anchor\":\"x\",\"domain\":[0.0,1.0],\"title\":{\"text\":\"Loss\"}},\"xaxis2\":{\"anchor\":\"y2\",\"domain\":[0.55,1.0],\"title\":{\"text\":\"Epochs\"}},\"yaxis2\":{\"anchor\":\"x2\",\"domain\":[0.0,1.0],\"title\":{\"text\":\"Accuracy\"}},\"annotations\":[{\"font\":{\"size\":16},\"showarrow\":false,\"text\":\"Loss\",\"x\":0.225,\"xanchor\":\"center\",\"xref\":\"paper\",\"y\":1.0,\"yanchor\":\"bottom\",\"yref\":\"paper\"},{\"font\":{\"size\":16},\"showarrow\":false,\"text\":\"Accuracy\",\"x\":0.775,\"xanchor\":\"center\",\"xref\":\"paper\",\"y\":1.0,\"yanchor\":\"bottom\",\"yref\":\"paper\"}],\"title\":{\"text\":\"Training History\"},\"hovermode\":\"x unified\"}}",
			"confusion_matrix": "{\"data\":[{\"colorscale\":[[0.0,\"rgb(247,251,255)\"],[0.125,\"rgb(222,235,247)\"],[0.25,\"rgb(198,219,239)\"],[0.375,\"rgb(158,202,225)\"],[0.5,\"rgb(107,174,214)\"],[0.625,\"rgb(66,146,198)\"],[0.75,\"rgb(33,113,181)\"],[0.875,\"rgb(8,81,156)\"],[1.0,\"rgb(8,48,107)\"]],\"text\":{\"dtype\":\"i1\",\"bdata\":\"BwAAAAgAAAAF\",\"shape\":\"3, 3\"},\"texttemplate\":\"%{text}\",\"x\":[\"Bachelor\",\"Master\",\"PhD\"],\"y\":[\"Bachelor\",\"Master\",\"PhD\"],\"z\":{\"dtype\":\"i1\",\"bdata\":\"BwAAAAgAAAAF\",\"shape\":\"3, 3\"},\"type\":\"heatmap\"}],\"layout\":{\"template\":{\"data\":{\"histogram2dcontour\":[{\"type\":\"histogram2dcontour\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"choropleth\":[{\"type\":\"choropleth\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"histogram2d\":[{\"type\":\"histogram2d\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"heatmap\":[{\"type\":\"heatmap\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"contourcarpet\":[{\"type\":\"contourcarpet\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"contour\":[{\"type\":\"contour\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"surface\":[{\"type\":\"surface\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"mesh3d\":[{\"type\":\"mesh3d\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"scatter\":[{\"fillpattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2},\"type\":\"scatter\"}],\"parcoords\":[{\"type\":\"parcoords\",\"line\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterpolargl\":[{\"type\":\"scatterpolargl\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"bar\":[{\"error_x\":{\"color\":\"#2a3f5f\"},\"error_y\":{\"color\":\"#2a3f5f\"},\"marker\":{\"line\":{\"color\":\"#E5ECF6\",\"width\":0.5},\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"bar\"}],\"scattergeo\":[{\"type\":\"scattergeo\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterpolar\":[{\"type\":\"scatterpolar\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"histogram\":[{\"marker\":{\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"histogram\"}],\"scattergl\":[{\"type\":\"scattergl\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatter3d\":[{\"type\":\"scatter3d\",\"line\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}},\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattermap\":[{\"type\":\"scattermap\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattermapbox\":[{\"type\":\"scattermapbox\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterternary\":[{\"type\":\"scatterternary\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattercarpet\":[{\"type\":\"scattercarpet\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"carpet\":[{\"aaxis\":{\"endlinecolor\":\"#2a3f5f\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"minorgridcolor\":\"white\",\"startlinecolor\":\"#2a3f5f\"},\"baxis\":{\"endlinecolor\":\"#2a3f5f\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"minorgridcolor\":\"white\",\"startlinecolor\":\"#2a3f5f\"},\"type\":\"carpet\"}],\"table\":[{\"cells\":{\"fill\":{\"color\":\"#EBF0F8\"},\"line\":{\"color\":\"white\"}},\"header\":{\"fill\":{\"color\":\"#C8D4E3\"},\"line\":{\"color\":\"white\"}},\"type\":\"table\"}],\"barpolar\":[{\"marker\":{\"line\":{\"color\":\"#E5ECF6\",\"width\":0.5},\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"barpolar\"}],\"pie\":[{\"automargin\":true,\"type\":\"pie\"}]},\"layout\":{\"autotypenumbers\":\"strict\",\"colorway\":[\"#636efa\",\"#EF553B\",\"#00cc96\",\"#ab63fa\",\"#FFA15A\",\"#19d3f3\",\"#FF6692\",\"#B6E880\",\"#FF97FF\",\"#FECB52\"],\"font\":{\"color\":\"#2a3f5f\"},\"hovermode\":\"closest\",\"hoverlabel\":{\"align\":\"left\"},\"paper_bgcolor\":\"white\",\"plot_bgcolor\":\"#E5ECF6\",\"polar\":{\"bgcolor\":\"#E5ECF6\",\"angularaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"radialaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"}},\"ternary\":{\"bgcolor\":\"#E5ECF6\",\"aaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"baxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"caxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"}},\"coloraxis\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}},\"colorscale\":{\"sequential\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]],\"sequentialminus\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]],\"diverging\":[[0,\"#8e0152\"],[0.1,\"#c51b7d\"],[0.2,\"#de77ae\"],[0.3,\"#f1b6da\"],[0.4,\"#fde0ef\"],[0.5,\"#f7f7f7\"],[0.6,\"#e6f5d0\"],[0.7,\"#b8e186\"],[0.8,\"#7fbc41\"],[0.9,\"#4d9221\"],[1,\"#276419\"]]},\"xaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\",\"title\":{\"standoff\":15},\"zerolinecolor\":\"white\",\"automargin\":true,\"zerolinewidth\":2},\"yaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\",\"title\":{\"standoff\":15},\"zerolinecolor\":\"white\",\"automargin\":true,\"zerolinewidth\":2},\"scene\":{\"xaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2},\"yaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2},\"zaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2}},\"shapedefaults\":{\"line\":{\"color\":\"#2a3f5f\"}},\"annotationdefaults\":{\"arrowcolor\":\"#2a3f5f\",\"arrowhead\":0,\"arrowwidth\":1},\"geo\":{\"bgcolor\":\"white\",\"landcolor\":\"#E5ECF6\",\"subunitcolor\":\"white\",\"showland\":true,\"showlakes\":true,\"lakecolor\":\"white\"},\"title\":{\"x\":0.05},\"mapbox\":{\"style\":\"light\"}}},\"title\":{\"text\":\"Confusion Matrix\"},\"xaxis\":{\"title\":{\"text\":\"Predicted Label\"}},\"yaxis\":{\"title\":{\"text\":\"True Label\"}}}}",
			"feature_importance": "{\"data\":[{\"marker\":{\"color\":\"skyblue\"},\"orientation\":\"h\",\"x\":{\"dtype\":\"f4\",\"bdata\":\"VkcjPhRGSz6cRSA+\"},\"y\":[\"yearsexperience\",\"salary\",\"age\"],\"type\":\"bar\"}],\"layout\":{\"template\":{\"data\":{\"histogram2dcontour\":[{\"type\":\"histogram2dcontour\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"choropleth\":[{\"type\":\"choropleth\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"histogram2d\":[{\"type\":\"histogram2d\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"heatmap\":[{\"type\":\"heatmap\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"contourcarpet\":[{\"type\":\"contourcarpet\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"contour\":[{\"type\":\"contour\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"surface\":[{\"type\":\"surface\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"},\"colorscale\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]]}],\"mesh3d\":[{\"type\":\"mesh3d\",\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}],\"scatter\":[{\"fillpattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2},\"type\":\"scatter\"}],\"parcoords\":[{\"type\":\"parcoords\",\"line\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterpolargl\":[{\"type\":\"scatterpolargl\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"bar\":[{\"error_x\":{\"color\":\"#2a3f5f\"},\"error_y\":{\"color\":\"#2a3f5f\"},\"marker\":{\"line\":{\"color\":\"#E5ECF6\",\"width\":0.5},\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"bar\"}],\"scattergeo\":[{\"type\":\"scattergeo\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterpolar\":[{\"type\":\"scatterpolar\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"histogram\":[{\"marker\":{\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"histogram\"}],\"scattergl\":[{\"type\":\"scattergl\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatter3d\":[{\"type\":\"scatter3d\",\"line\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}},\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattermap\":[{\"type\":\"scattermap\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattermapbox\":[{\"type\":\"scattermapbox\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scatterternary\":[{\"type\":\"scatterternary\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"scattercarpet\":[{\"type\":\"scattercarpet\",\"marker\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}}}],\"carpet\":[{\"aaxis\":{\"endlinecolor\":\"#2a3f5f\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"minorgridcolor\":\"white\",\"startlinecolor\":\"#2a3f5f\"},\"baxis\":{\"endlinecolor\":\"#2a3f5f\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"minorgridcolor\":\"white\",\"startlinecolor\":\"#2a3f5f\"},\"type\":\"carpet\"}],\"table\":[{\"cells\":{\"fill\":{\"color\":\"#EBF0F8\"},\"line\":{\"color\":\"white\"}},\"header\":{\"fill\":{\"color\":\"#C8D4E3\"},\"line\":{\"color\":\"white\"}},\"type\":\"table\"}],\"barpolar\":[{\"marker\":{\"line\":{\"color\":\"#E5ECF6\",\"width\":0.5},\"pattern\":{\"fillmode\":\"overlay\",\"size\":10,\"solidity\":0.2}},\"type\":\"barpolar\"}],\"pie\":[{\"automargin\":true,\"type\":\"pie\"}]},\"layout\":{\"autotypenumbers\":\"strict\",\"colorway\":[\"#636efa\",\"#EF553B\",\"#00cc96\",\"#ab63fa\",\"#FFA15A\",\"#19d3f3\",\"#FF6692\",\"#B6E880\",\"#FF97FF\",\"#FECB52\"],\"font\":{\"color\":\"#2a3f5f\"},\"hovermode\":\"closest\",\"hoverlabel\":{\"align\":\"left\"},\"paper_bgcolor\":\"white\",\"plot_bgcolor\":\"#E5ECF6\",\"polar\":{\"bgcolor\":\"#E5ECF6\",\"angularaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"radialaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"}},\"ternary\":{\"bgcolor\":\"#E5ECF6\",\"aaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"baxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"},\"caxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\"}},\"coloraxis\":{\"colorbar\":{\"outlinewidth\":0,\"ticks\":\"\"}},\"colorscale\":{\"sequential\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]],\"sequentialminus\":[[0.0,\"#0d0887\"],[0.1111111111111111,\"#46039f\"],[0.2222222222222222,\"#7201a8\"],[0.3333333333333333,\"#9c179e\"],[0.4444444444444444,\"#bd3786\"],[0.5555555555555556,\"#d8576b\"],[0.6666666666666666,\"#ed7953\"],[0.7777777777777778,\"#fb9f3a\"],[0.8888888888888888,\"#fdca26\"],[1.0,\"#f0f921\"]],\"diverging\":[[0,\"#8e0152\"],[0.1,\"#c51b7d\"],[0.2,\"#de77ae\"],[0.3,\"#f1b6da\"],[0.4,\"#fde0ef\"],[0.5,\"#f7f7f7\"],[0.6,\"#e6f5d0\"],[0.7,\"#b8e186\"],[0.8,\"#7fbc41\"],[0.9,\"#4d9221\"],[1,\"#276419\"]]},\"xaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\",\"title\":{\"standoff\":15},\"zerolinecolor\":\"white\",\"automargin\":true,\"zerolinewidth\":2},\"yaxis\":{\"gridcolor\":\"white\",\"linecolor\":\"white\",\"ticks\":\"\",\"title\":{\"standoff\":15},\"zerolinecolor\":\"white\",\"automargin\":true,\"zerolinewidth\":2},\"scene\":{\"xaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2},\"yaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2},\"zaxis\":{\"backgroundcolor\":\"#E5ECF6\",\"gridcolor\":\"white\",\"linecolor\":\"white\",\"showbackground\":true,\"ticks\":\"\",\"zerolinecolor\":\"white\",\"gridwidth\":2}},\"shapedefaults\":{\"line\":{\"color\":\"#2a3f5f\"}},\"annotationdefaults\":{\"arrowcolor\":\"#2a3f5f\",\"arrowhead\":0,\"arrowwidth\":1},\"geo\":{\"bgcolor\":\"white\",\"landcolor\":\"#E5ECF6\",\"subunitcolor\":\"white\",\"showland\":true,\"showlakes\":true,\"lakecolor\":\"white\"},\"title\":{\"x\":0.05},\"mapbox\":{\"style\":\"light\"}}},\"title\":{\"text\":\"Feature Importance (First Layer Weights)\"},\"xaxis\":{\"title\":{\"text\":\"Importance Score\"}},\"yaxis\":{\"title\":{\"text\":\"Features\"}}}}"
		},
		"summary": {
			"metrics": {
				"accuracy": 1.0,
				"precision_micro": 1.0,
				"precision_macro": 1.0,
				"precision_weighted": 1.0,
				"recall_micro": 1.0,
				"recall_macro": 1.0,
				"recall_weighted": 1.0
			},
			"model_summary": {
				"architecture": [
					{
						"name": "dense",
						"trainable": true,
						"dtype": {
							"module": "keras",
							"class_name": "DTypePolicy",
							"config": {
								"name": "float32"
							},
							"registered_name": null
						},
						"units": 64,
						"activation": "relu",
						"use_bias": true,
						"kernel_initializer": {
							"module": "keras.initializers",
							"class_name": "GlorotUniform",
							"config": {
								"seed": null
							},
							"registered_name": null
						},
						"bias_initializer": {
							"module": "keras.initializers",
							"class_name": "Zeros",
							"config": {},
							"registered_name": null
						},
						"kernel_regularizer": null,
						"bias_regularizer": null,
						"kernel_constraint": null,
						"bias_constraint": null
					},
					{
						"name": "dense_1",
						"trainable": true,
						"dtype": {
							"module": "keras",
							"class_name": "DTypePolicy",
							"config": {
								"name": "float32"
							},
							"registered_name": null
						},
						"units": 32,
						"activation": "relu",
						"use_bias": true,
						"kernel_initializer": {
							"module": "keras.initializers",
							"class_name": "GlorotUniform",
							"config": {
								"seed": null
							},
							"registered_name": null
						},
						"bias_initializer": {
							"module": "keras.initializers",
							"class_name": "Zeros",
							"config": {},
							"registered_name": null
						},
						"kernel_regularizer": null,
						"bias_regularizer": null,
						"kernel_constraint": null,
						"bias_constraint": null
					},
					{
						"name": "dropout",
						"trainable": true,
						"dtype": {
							"module": "keras",
							"class_name": "DTypePolicy",
							"config": {
								"name": "float32"
							},
							"registered_name": null
						},
						"rate": 0.2,
						"seed": null,
						"noise_shape": null
					},
					{
						"name": "dense_2",
						"trainable": true,
						"dtype": {
							"module": "keras",
							"class_name": "DTypePolicy",
							"config": {
								"name": "float32"
							},
							"registered_name": null
						},
						"units": 3,
						"activation": "softmax",
						"use_bias": true,
						"kernel_initializer": {
							"module": "keras.initializers",
							"class_name": "GlorotUniform",
							"config": {
								"seed": null
							},
							"registered_name": null
						},
						"bias_initializer": {
							"module": "keras.initializers",
							"class_name": "Zeros",
							"config": {},
							"registered_name": null
						},
						"kernel_regularizer": null,
						"bias_regularizer": null,
						"kernel_constraint": null,
						"bias_constraint": null
					}
				],
				"input_shape": [
					null,
					3
				],
				"output_shape": [
					null,
					3
				],
				"class_names": [
					"Bachelor",
					"Master",
					"PhD"
				],
				"training_epochs": 76,
				"model_info": {
					"storage_path": "neural_networks/Neural_network_245_35ff1cb1-12a1-4be7-a200-3c333165e6fb.keras",
					"bucket": "age-vista-data",
					"model_name": "Neural_network_245_35ff1cb1-12a1-4be7-a200-3c333165e6fb"
				},
				"data_type": "tabular"
			}
		},
		"title": "Neural_network_245",
		"analysis_group": "advance",
		"data_type": "tabular",
		"ai_report": "Here's a simple and easy-to-understand summary of the data insights:\n\n**Model Performance:**\n- **Accuracy:** 1.0 (perfect accuracy)\n- **Precision:** 1.0 (micro, macro, and weighted) - the model is precise in all classes\n- **Recall:** 1.0 (micro, macro, and weighted) - the model correctly identifies all instances of each class\n\n**Model Architecture:**\n- **Layers:** \n  1. Dense (64 units, ReLU activation)\n  2. Dense (32 units, ReLU activation)\n  3. Dropout (20% rate)\n  4. Dense (3 units, Softmax activation for 3 classes)\n- **Input Shape:** (None, 3) - the model accepts 3 features\n- **Output Shape:** (None, 3) - the model predicts 3 classes\n\n**Model Details:**\n- **Training Epochs:** 76\n- **Classes:** Bachelor, Master, PhD\n- **Model Storage:** neural_networks/Neural_network_245_35ff1cb1-12a1-4be7-a200-3c333165e6fb.keras in the 'age-vista-data' bucket\n\n**Data Type:** Tabular data\n\nThis summary provides an overview of the model's performance, architecture, and training details. Let me know if you'd like me to add or clarify anything!",
		"id": "a6d44eaa-b037-462a-a7a0-bc84aedd9506",
		"created_at": "2025-06-06T10:55:18.290818Z",
		"updated_at": "2025-06-06T10:55:18.290888Z",
		"_class_": "Report"
	}
}

```