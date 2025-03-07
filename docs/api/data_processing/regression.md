## Endpoint

`POST /data-processing/regression`

## Description

This endpoint performs regression analysis using different regression strategies (linear, decision tree, or logistic). The request should include the regression type, features, target variable, and the data file.

## Request

The request should be made with `Content-Type: multipart/form-data` and include the following parameters:

### Form Data Parameters

| Name            | Type   | Required | Description                                                                 |
| --------------- | ------ | -------- | --------------------------------------------------------------------------- |
| `regression_type` | string | Yes      | The type of regression to perform (`linear`, `decision_tree`, or `logistic`). |
| `features_col`  | string | Yes      | Comma-separated list of feature columns (independent variables).             |
| `target_col`    | string | Yes      | The target column (dependent variable).                                      |
| `file`          | file   | Yes      | The data file to be used for regression analysis (CSV format).               |

## Response

### Success Response

- **Status Code:** `200 OK`
- **Body:** A JSON object containing the regression results. The structure of the response depends on the regression type.

#### Linear Regression Response

```json
{
  "RMSE": "number",
  "R2": "number",
  "Coefficients": ["number"],
  "Intercept": "number"
}
```

#### Decision Tree Regression Response
```json

{
  "RMSE": "number",
  "R2": "number",
  "Feature Importances": ["number"]
}
```

#### Logistic Regression Response

```json

{
  "Accuracy": "number",
  "Precision": "number",
  "Recall": "number",
  "F1 Score": "number"
}

```