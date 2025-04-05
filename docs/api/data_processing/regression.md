## Endpoint

`POST /data-processing/regression`

## Description

This endpoint performs regression analysis using different regression strategies (linear, decision tree, or logistic). The request should include the regression type, features, target variable, and the data file.

## Request

The request should be made with `Content-Type: json` and include the following parameters:

### Form Data Parameters

| Name            | Type   | Required | Description                                                                 |
| --------------- | ------ | -------- | --------------------------------------------------------------------------- |
| `title` | string | Yes      | The Title or Name for the Analysis e.g (Regression Analysis Report) |
| `regression_type` | string | Yes      | The type of regression to perform (`linear`, `decision_tree`, or `logistic`). |
| `features_col`  | array | Yes      | list of feature columns (independent variables).             |
| `target_col`    | string | Yes      | The target column (dependent variable).                                      |
| `file_id`          | str   | Yes      | The unique identifier for the file to be analyzed.               |
| `columns`          | str   | No     | A list of selected columns to run your analysis on              |


### Example Request Body
```json
{
	"file_id": "ba9b5b9f-3d2e-4b7a-b3e1-53eb8212698b",
	"regression_type": "linear",
	"features_col": ["feature1", "feature2", "feature3"],
	"label_col": "target"
}
```

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the regression results. The structure of the response depends on the regression type.

#### Linear Regression Response

```json
{
  "status": "sucess",
  "message":"Regression performed successfully",
   "data": {
    "RMSE": "number",
    "R2": "number",
    "Coefficients": ["number"],
    "Intercept": "number"
  }
}
```

#### Decision Tree Regression Response
```json
...
{
  "RMSE": "number",
  "R2": "number",
  "Feature Importances": ["number"],
  "Depth": "number",
  "R2": "number",
}
```

#### Logistic Regression Response

```json
...
{
  "Intercept": ["number"],
  "Score": "number",
  "Coefficients": ["number"],
}

```