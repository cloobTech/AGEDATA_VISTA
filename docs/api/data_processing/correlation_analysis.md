### CorrelationAnalysisInput Schema

**Description:**  
The `CorrelationAnalysisInput` schema is used for performing correlation analysis on a dataset. It allows users to specify the numeric columns to include in the analysis, the correlation method, and whether to compute p-values.

---

## Fields

| Field Name        | Type        | Default Value | Required | Description                                                                 |
| ----------------- | ----------- | ------------- | -------- | --------------------------------------------------------------------------- |
| `numeric_cols`    | `list[str]` |               | Yes      | A list of column names to be included in the correlation analysis.          |
| `method`          | `str`       | `"pearson"`   | No       | The correlation method to use (`pearson`, `kendall`, or `spearman`).        |
| `compute_p_values`| `bool`      | `False`       | No       | Whether to compute p-values for the correlation coefficients.               |

---

## Example Usage

### Example Request Body

```json
{
  "numeric_cols": ["age", "salary", "experience"],
  "method": "spearman",
  "compute_p_values": true
}
```

---

### Full Request Body Example

```json
{
  "columns": ["age", "salary", "experience"],
  "analysis_type": "correlation",
  "analysis_group": "multi_variate",
  "generate_visualizations": true,
  "title": "Correlation Analysis Example",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "numeric_cols": ["age", "salary", "experience"],
    "method": "spearman",
    "compute_p_values": true
  }
}
```

`NOTE: visualization is automatic, all you need to do is set "{generate_visualizations": true}" and it will create a correlation matrix visualization`