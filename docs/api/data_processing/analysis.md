## Endpoint

`POST BASE_URL/api/v1/analysis`

# AnalysisInput Schema Documentation

## Description

The `AnalysisInput` schema is a base model used for performing various types of data analysis. It supports both regression and descriptive analysis and includes options for generating visualizations.

---

## Fields

| Field Name                | Type                                            | Default Value       | Required | Description                                                          |
| ------------------------- | ----------------------------------------------- | ------------------- | -------- | -------------------------------------------------------------------- |
| `columns`                 | `list`                                          | `[]`                | No       | A list of columns to include in the analysis.                        |
| `analysis_type`           | `str`                                           |                     | Yes      | The type of analysis to perform (e.g., `regression`, `descriptive`). |
| `generate_visualizations` | `bool`                                          | `False`             | No       | Whether to generate visualizations for the analysis.                 |
| `analysis_input`          | `RegressionInput` or `DescriptiveAnalysisInput` |                     | Yes      | The specific input parameters for the selected analysis type.        |
| `title`                   | `str`                                           | `"Analysis Report"` | No       | The title of the analysis report.                                    |
| `project_id`              | `str`                                           |                     | Yes      | The unique identifier for the project associated with the analysis.  |
| `file_id`                 | `str`                                           |                     | Yes      | The unique identifier for the file to be analyzed.                   |

---

## Example Usage

### Example Request Body for Regression Analysis

```json
{
  "columns": ["feature1", "feature2", "target"],
  "analysis_type": "regression",
  "generate_visualizations": true,
  "analysis_input": {
    "regression_type": "linear",
    "features_col": ["feature1", "feature2"],
    "label_col": "target"
  },
  "title": "Regression Analysis Report",
  "project_id": "12345",
  "file_id": "67890"
}
```
