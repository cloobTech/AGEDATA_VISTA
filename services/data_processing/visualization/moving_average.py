import plotly.graph_objects as go
import pandas as pd


def generate_ma_visualizations(
    original: pd.Series,
    moving_avg: pd.Series,
    ma_type: str,
    window_size: int
) -> dict:
    """Generate moving average visualizations"""
    visuals = {}
    
    fig = go.Figure()
    
    # Original series
    fig.add_trace(go.Scatter(
        x=original.index,
        y=original,
        name="Original",
        line=dict(color='blue'),
        opacity=0.6
    ))
    
    # Moving average
    fig.add_trace(go.Scatter(
        x=moving_avg.index,
        y=moving_avg,
        name=f"{ma_type.capitalize()} MA ({window_size})",
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title=f"{ma_type.capitalize()} Moving Average",
        xaxis_title="Time",
        yaxis_title="Value",
        hovermode="x unified"
    )
    
    visuals["moving_average_plot"] = fig.to_json()
    return visuals


