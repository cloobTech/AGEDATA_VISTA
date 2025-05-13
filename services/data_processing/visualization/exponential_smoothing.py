import plotly.graph_objects as go
import pandas as pd


def generate_es_visualizations(
    original: pd.Series,
    fitted: pd.Series,
    model_type: str
) -> dict:
    """Generate exponential smoothing visualizations"""
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
    
    # Fitted values
    fig.add_trace(go.Scatter(
        x=fitted.index,
        y=fitted,
        name=f"Fitted ({model_type})",
        line=dict(color='green', width=2)
    ))
    
    fig.update_layout(
        title=f"Exponential Smoothing ({model_type})",
        xaxis_title="Time",
        yaxis_title="Value",
        hovermode="x unified"
    )
    
    visuals["smoothing_plot"] = fig.to_json()
    
    # Residuals plot
    residuals = original - fitted
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=residuals.index,
        y=residuals,
        mode='markers',
        name="Residuals"
    ))
    fig.add_hline(y=0, line_dash="dash")
    fig.update_layout(
        title="Smoothing Residuals",
        xaxis_title="Time",
        yaxis_title="Residual Value"
    )
    visuals["residuals_plot"] = fig.to_json()
    
    return visuals