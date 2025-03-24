import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from schemas.descriptive_visualization import DescriptiveVisualizations


def pie_chart_visualization(df: pd.DataFrame, inputs: DescriptiveVisualizations):
    pie_chart_input = inputs.pie_chart_input
    pie_chart = px.pie(df, **pie_chart_input.model_dump())
    return pie_chart


def bar_chart_visualization(df: pd.DataFrame, inputs: DescriptiveVisualizations):
    bar_chart_input = inputs.bar_chart_input
    bar_chart = px.bar(df, **bar_chart_input.model_dump())
    return bar_chart


def line_chart_visualization(df: pd.DataFrame, inputs: DescriptiveVisualizations):
    line_chart_input = inputs.line_chart_input
    line_chart = px.line(df, **line_chart_input.model_dump())
    return line_chart


def scatter_plot_visualization(df: pd.DataFrame, inputs: DescriptiveVisualizations):
    scatter_plot_input = inputs.scatter_plot_input
    scatter_plot = px.scatter(df, **scatter_plot_input.model_dump())
    return scatter_plot


def heat_map_visualization(df: pd.DataFrame, inputs: DescriptiveVisualizations):
    heat_map_input = inputs.heat_map_input
    heat_map = px.density_heatmap(df, **heat_map_input.model_dump())
    return heat_map


def histogram_visualization(df: pd.DataFrame, inputs: DescriptiveVisualizations):
    histogram_input = inputs.histogram_input
    histogram = px.histogram(df, **histogram_input.model_dump())
    return histogram


chart_functions = {
    "pie_chart": pie_chart_visualization,
    "bar_chart": bar_chart_visualization,
    "line_chart": line_chart_visualization,
    "scatter_plot": scatter_plot_visualization,
    "heat_map": heat_map_visualization,
    "histogram": histogram_visualization
}


def generate_descriptive_visualizations(df, inputs: DescriptiveVisualizations, visualization_list: list) -> dict:
    """
    Generate descriptive visualizations based on the input parameters."""
    visualizations = {}
    for visualization in visualization_list:
        if visualization not in chart_functions:
            continue
        chart = chart_functions[visualization](df, inputs)
        visualizations[visualization] = pio.to_json(chart)
    return visualizations
