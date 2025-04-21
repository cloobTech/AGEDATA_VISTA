# Descriptive Analysis Input Schema Documentation

## Description

The `DescriptiveAnalysisInput` schema is used for performing descriptive analysis on a dataset. It allows users to specify a list of visualizations to generate and provides detailed configuration options for each type of visualization.

---

## Fields

### DescriptiveAnalysisInput

| Field Name                   | Type                        | Default Value | Required | Description                                                            |
| ---------------------------- | --------------------------- | ------------- | -------- | ---------------------------------------------------------------------- |
| `visualization_list`         | `list`                      | `[]`          | No       | A list of visualizations to generate (e.g., `pie_chart`, `bar_chart`). |
| `descriptive_visualizations` | `DescriptiveVisualizations` | `None`        | No       | Detailed configuration for each visualization type.                    |

---

## Visualization Input Schemas

### PieChartInputSchema

| Field Name | Type    | Default Value | Required | Description                                               |
| ---------- | ------- | ------------- | -------- | --------------------------------------------------------- |
| `names`    | `str`   |               | Yes      | The column name for the pie chart categories.             |
| `title`    | `str`   |               | Yes      | The title of the pie chart.                               |
| `subtitle` | `str`   | `None`        | No       | The subtitle of the pie chart.                            |
| `hole`     | `float` | `None`        | No       | The size of the hole in the pie chart (for donut charts). |
| `color`    | `str`   | `None`        | No       | The column name for color coding.                         |

---

### BarChartInputSchema

| Field Name | Type  | Default Value | Required | Description                                         |
| ---------- | ----- | ------------- | -------- | --------------------------------------------------- |
| `x`        | `str` |               | Yes      | The column name for the x-axis.                     |
| `y`        | `str` |               | Yes      | The column name for the y-axis.                     |
| `title`    | `str` |               | Yes      | The title of the bar chart.                         |
| `subtitle` | `str` | `None`        | No       | The subtitle of the bar chart.                      |
| `color`    | `str` | `None`        | No       | The column name for color coding.                   |
| `barmode`  | `str` | `None`        | No       | The mode of the bar chart (e.g., `group`, `stack`). |

---

### LineChartInputSchema

| Field Name | Type  | Default Value | Required | Description                     |
| ---------- | ----- | ------------- | -------- | ------------------------------- |
| `x`        | `str` |               | Yes      | The column name for the x-axis. |
| `y`        | `str` |               | Yes      | The column name for the y-axis. |
| `title`    | `str` |               | Yes      | The title of the line chart.    |
| `subtitle` | `str` | `None`        | No       | The subtitle of the line chart. |

---

### HistogramInputSchema

| Field Name | Type  | Default Value | Required | Description                                         |
| ---------- | ----- | ------------- | -------- | --------------------------------------------------- |
| `x`        | `str` |               | Yes      | The column name for the x-axis.                     |
| `y`        | `str` |               | Yes      | The column name for the y-axis.                     |
| `title`    | `str` |               | Yes      | The title of the histogram.                         |
| `subtitle` | `str` | `None`        | No       | The subtitle of the histogram.                      |
| `color`    | `str` | `None`        | No       | The column name for color coding.                   |
| `barmode`  | `str` | `None`        | No       | The mode of the histogram (e.g., `group`, `stack`). |

---

### ScatterPlotInputSchema

| Field Name | Type  | Default Value | Required | Description                       |
| ---------- | ----- | ------------- | -------- | --------------------------------- |
| `x`        | `str` |               | Yes      | The column name for the x-axis.   |
| `y`        | `str` |               | Yes      | The column name for the y-axis.   |
| `title`    | `str` | `None`        | No       | The title of the scatter plot.    |
| `subtitle` | `str` | `None`        | No       | The subtitle of the scatter plot. |
| `color`    | `str` | `None`        | No       | The column name for color coding. |

---

### HeatMapSchema

| Field Name | Type  | Default Value | Required | Description                     |
| ---------- | ----- | ------------- | -------- | ------------------------------- |
| `x`        | `str` |               | Yes      | The column name for the x-axis. |
| `y`        | `str` |               | Yes      | The column name for the y-axis. |
| `title`    | `str` | `None`        | No       | The title of the heat map.      |
| `subtitle` | `str` | `None`        | No       | The subtitle of the heat map.   |

---

### DescriptiveVisualizations

| Field Name           | Type                     | Default Value | Required | Description                         |
| -------------------- | ------------------------ | ------------- | -------- | ----------------------------------- |
| `pie_chart_input`    | `PieChartInputSchema`    | `None`        | No       | Configuration for the pie chart.    |
| `line_chart_input`   | `LineChartInputSchema`   | `None`        | No       | Configuration for the line chart.   |
| `scatter_plot_input` | `ScatterPlotInputSchema` | `None`        | No       | Configuration for the scatter plot. |
| `bar_chart_input`    | `BarChartInputSchema`    | `None`        | No       | Configuration for the bar chart.    |
| `histogram_input`    | `HistogramInputSchema`   | `None`        | No       | Configuration for the histogram.    |
| `heat_map_input`     | `HeatMapSchema`          | `None`        | No       | Configuration for the heat map.     |

---

## Example Usage

### Example Of Request Body - used as an arguement of the data analysis request body for running a descriptive analysis

```json
{
  "visualization_list": ["pie_chart", "bar_chart"],
  "descriptive_visualizations": {
    "pie_chart_input": {
      "names": "department",
      "title": "Department Distribution",
      "subtitle": "Distribution of employees by department",
      "hole": 0.4,
      "color": "gender"
    },
    "bar_chart_input": {
      "x": "department",
      "y": "salary",
      "title": "Average Salary by Department",
      "subtitle": "Grouped by gender",
      "color": "gender",
      "barmode": "group"
    }
  }
}
```

### The is what the entire body may look like from the frontend. noticed that the descriptive analysis body was provided as as value for `analysis_input`

```json
{
  "columns": ["educationlevel", "salary", "age"],
  "analysis_type": "descriptive",
  "generate_visualizations": true,
  "title": "Report Test",
  "file_id": "e8952875-7afe-4b85-8c0b-c683dfeac357",
  "project_id": "9b17ff0d-1d15-420c-a24d-9fad6c5fff19",
  "analysis_input": {
    "visualization_list": [
      "bar_chart",
      "pie_chart",
      "line_chart",
      "scatter_plot",
      "heat_map",
      "histogram"
    ],
    "descriptive_visualizations": {
      "pie_chart_input": {
        "names": "educationlevel",
        "title": "Employee Distribution"
      },
      "bar_chart_input": {
        "x": "educationlevel",
        "y": "salary",
        "title": "Average Salary by Department"
      },
      "line_chart_input": {
        "x": "salary",
        "y": "age",
        "title": "Age vs Salary"
      },
      "scatter_plot_input": {
        "x": "salary",
        "y": "age",
        "title": "Age vs Salary"
      },
      "heat_map_input": {
        "x": "educationlevel",
        "y": "salary",
        "title": "Age Distribution"
      },
      "histogram_input": {
        "x": "educationlevel",
        "y": "salary",
        "title": "Age Distribution"
      }
    }
  }
}
```
