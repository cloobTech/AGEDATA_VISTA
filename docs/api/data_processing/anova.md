### Anova Input Schema

**Description:**  
The `Anova` schema is used for performing ANOVA (Analysis of Variance) analysis on a dataset. It allows users to specify the factors, dependent variable, and additional options such as interaction terms and effect sizes.

---

## Fields

| Field Name               | Type        | Default Value | Required | Description                                                           |
| ------------------------ | ----------- | ------------- | -------- | --------------------------------------------------------------------- |
| `factor_cols`            | `list[str]` |               | Yes      | A list of column names to be used as factors (categorical variables). |
| `value_col`              | `str`       |               | Yes      | The column name to be used as the dependent variable.                 |
| `include_interactions`   | `bool`      | `False`       | No       | Whether to include interaction terms in the analysis.                 |
| `calculate_effect_sizes` | `bool`      | `False`       | No       | Whether to compute effect sizes for the factors.                      |

---

## Example Usage

### Example Request Body

```json
{
  "factor_cols": ["department", "gender"],
  "value_col": "salary",
  "include_interactions": false,
  "calculate_effect_sizes": false
}
```

`NOTE: for one way anova -- include just a single col in the factor_cols e.g. "factor_cols": ["department"]`

### The is what the entire body may look like from the frontend. noticed that the anova analysis body was provided as as value for `analysis_input`

```json
{
  "columns": ["educationlevel", "salary", "age"],
  "analysis_type": "descriptive",
  "generate_visualizations": true,
  "title": "Report Test",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "factor_cols": ["department", "gender"],
    "value_col": "salary",
    "include_interactions": true,
    "calculate_effect_sizes": true
  }
}
```

`NOTE: visualization is automatic, all you need to is set "{generate_visualizations": true}"`
