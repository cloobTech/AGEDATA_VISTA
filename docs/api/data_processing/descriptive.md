# Descriptive Analysis API

## Endpoint: `/api/v1/data-processing/descriptive-analysis`

### Method: `POST`

### Description:

Perform descriptive analysis on the provided dataset.

### Request Body:

The request body should be a JSON object that adheres to the following schema:

#### Descriptive Analysis Inputs/Params

| Field                        | Type                        | Required | Default | Description                                                                                                                       |
| ---------------------------- | --------------------------- | -------- | ------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `title`                      | `str`                       | Yes      | -       | A unique name identifier for the analysis.                                                                                        |
| `file_id`                    | `str`                       | Yes      | -       | The unique identifier for the file to be analyzed.                                                                                |
| `project_id`                 | `str`                       | Yes      | -       | The unique identifier for the project associated with the analysis.                                                               |
| `columns`                    | `str`                       | No       | `[] `   | A list of selected columns to run your analysis on.                                                                               |
| `generate_visualizations`    | `bool`                      | No       | `False` | Whether to generate visualizations for the analysis.                                                                              |
| `visualization_list`         | `list`                      | No       | `[]`    | A list of visualizations to generate (e.g., `["bar_chart", "histogram", "pie_chart", "line_chart", "heat_map", "scatter_plot"]`). |
| `descriptive_visualizations` | `DescriptiveVisualizations` | No       | `None`  | Configuration for the visualizations (e.g., chart inputs).                                                                        |
|                              |

## Schema: `DescriptiveVisualizations`

| Field                | Type                     | Required | Default | Description                                       |
| -------------------- | ------------------------ | -------- | ------- | ------------------------------------------------- |
| `pie_chart_input`    | `PieChartInputSchema`    | No       | `None`  | Configuration for the pie chart visualization.    |
| `line_chart_input`   | `LineChartInputSchema`   | No       | `None`  | Configuration for the line chart visualization.   |
| `scatter_plot_input` | `ScatterPlotInputSchema` | No       | `None`  | Configuration for the scatter plot visualization. |
| `bar_chart_input`    | `BarChartInputSchema`    | No       | `None`  | Configuration for the bar chart visualization.    |
| `histogram_input`    | `HistogramInputSchema`   | No       | `None`  | Configuration for the histogram visualization.    |
| `heat_map_input`     | `HeatMapSchema`          | No       | `None`  | Configuration for the heat map visualization.     |

---

## Nested Schemas

### 1. `PieChartInputSchema`

| Field      | Type    | Required | Default | Description                                        |
| ---------- | ------- | -------- | ------- | -------------------------------------------------- |
| `names`    | `str`   | Yes      | -       | Column name for the pie chart categories.          |
| `title`    | `str`   | Yes      | -       | Title of the pie chart.                            |
| `subtitle` | `str`   | No       | `None`  | Subtitle of the pie chart.                         |
| `hole`     | `float` | No       | `None`  | Size of the hole in the center (for donut charts). |
| `color`    | `str`   | No       | `None`  | Column name for color grouping.                    |

---

### 2. `BarChartInputSchema`

| Field      | Type  | Required | Default | Description                        |
| ---------- | ----- | -------- | ------- | ---------------------------------- |
| `x`        | `str` | Yes      | -       | Column name for the x-axis.        |
| `y`        | `str` | Yes      | -       | Column name for the y-axis.        |
| `title`    | `str` | Yes      | -       | Title of the bar chart.            |
| `subtitle` | `str` | No       | `None`  | Subtitle of the bar chart.         |
| `color`    | `str` | No       | `None`  | Column name for color grouping.    |
| `barmode`  | `str` | No       | `None`  | Bar mode (e.g., `group`, `stack`). |

---

### 3. `LineChartInputSchema`

| Field      | Type  | Required | Default | Description                 |
| ---------- | ----- | -------- | ------- | --------------------------- |
| `x`        | `str` | Yes      | -       | Column name for the x-axis. |
| `y`        | `str` | Yes      | -       | Column name for the y-axis. |
| `title`    | `str` | Yes      | -       | Title of the line chart.    |
| `subtitle` | `str` | No       | `None`  | Subtitle of the line chart. |

---

### 4. `ScatterPlotInputSchema`

| Field      | Type  | Required | Default | Description                     |
| ---------- | ----- | -------- | ------- | ------------------------------- |
| `x`        | `str` | Yes      | -       | Column name for the x-axis.     |
| `y`        | `str` | Yes      | -       | Column name for the y-axis.     |
| `title`    | `str` | No       | `None`  | Title of the scatter plot.      |
| `subtitle` | `str` | No       | `None`  | Subtitle of the scatter plot.   |
| `color`    | `str` | No       | `None`  | Column name for color grouping. |

---

### 5. `HistogramInputSchema`

| Field      | Type  | Required | Default | Description                        |
| ---------- | ----- | -------- | ------- | ---------------------------------- |
| `x`        | `str` | Yes      | -       | Column name for the x-axis.        |
| `y`        | `str` | Yes      | -       | Column name for the y-axis.        |
| `title`    | `str` | Yes      | -       | Title of the histogram.            |
| `subtitle` | `str` | No       | `None`  | Subtitle of the histogram.         |
| `color`    | `str` | No       | `None`  | Column name for color grouping.    |
| `barmode`  | `str` | No       | `None`  | Bar mode (e.g., `group`, `stack`). |

---

### 6. `HeatMapSchema`

| Field      | Type  | Required | Default | Description                 |
| ---------- | ----- | -------- | ------- | --------------------------- |
| `x`        | `str` | Yes      | -       | Column name for the x-axis. |
| `y`        | `str` | Yes      | -       | Column name for the y-axis. |
| `title`    | `str` | No       | `None`  | Title of the heat map.      |
| `subtitle` | `str` | No       | `None`  | Subtitle of the heat map.   |

---

### Example Request:

```json
{
  "file_id": "58cda8a8-0c80-4fcf-8ac1-774e862e000e",
  "project_id": "9b409528-2a59-4d92-a52e-496f6c215156",
  "generate_visualizations": true,
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
      "names": "Department",
      "title": "Employee Distribution"
    },
    "bar_chart_input": {
      "x": "Department",
      "y": "Salary",
      "title": "Average Salary by Department"
    },
    "line_chart_input": {
      "x": "Salary",
      "y": "Age",
      "title": "Age vs Salary"
    },
    "scatter_plot_input": {
      "x": "Salary",
      "y": "Age",
      "title": "Age vs Salary"
    },
    "heat_map_input": {
      "x": "Department",
      "y": "Salary",
      "title": "Age Distribution"
    },
    "histogram_input": {
      "x": "Department",
      "y": "Salary",
      "title": "Age Distribution"
    }
  }
}
```
