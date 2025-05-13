import numpy as np
import plotly.graph_objects as go


def generate_acf_pacf_visualizations(
    acf_values: np.ndarray,
    pacf_values: np.ndarray,
    acf_confint: np.ndarray,
    pacf_confint: np.ndarray,
    nlags: int,
    alpha: float
) -> dict:
    """Generate ACF and PACF visualizations"""
    visuals = {}
    
    # Create ACF plot
    fig = go.Figure()
    
    # Add ACF values as bars
    fig.add_trace(go.Bar(
        x=list(range(nlags+1)),
        y=acf_values,
        name="ACF",
        marker_color='blue'
    ))
    
    # Add confidence interval
    fig.add_trace(
        go.Scatter(
            x=list(range(nlags+1)),
            y=acf_confint[:, 0] - acf_values,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='none'
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=list(range(nlags+1)),
            y=acf_confint[:, 1] - acf_values,
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(0, 0, 255, 0.2)',
            fill='tonexty',
            name=f"{int((1-alpha)*100)}% Confidence",
            hoverinfo='none'
        )
    )
    
    # Add zero line
    fig.add_shape(
        type="line",
        x0=-1,
        y0=0,
        x1=nlags+1,
        y1=0,
        line=dict(color="black", width=1)
    )
    
    fig.update_layout(
        title=f"Autocorrelation (ACF)",
        xaxis_title="Lag",
        yaxis_title="ACF",
        hovermode="x",
        showlegend=True
    )
    
    visuals["acf_plot"] = fig.to_json()
    
    # Create PACF plot
    fig = go.Figure()
    
    # Add PACF values as bars
    fig.add_trace(go.Bar(
        x=list(range(nlags+1)),
        y=pacf_values,
        name="PACF",
        marker_color='green'
    ))
    
    # Add confidence interval
    fig.add_trace(
        go.Scatter(
            x=list(range(nlags+1)),
            y=pacf_confint[:, 0] - pacf_values,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='none'
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=list(range(nlags+1)),
            y=pacf_confint[:, 1] - pacf_values,
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(0, 255, 0, 0.2)',
            fill='tonexty',
            name=f"{int((1-alpha)*100)}% Confidence",
            hoverinfo='none'
        )
    )
    
    # Add zero line
    fig.add_shape(
        type="line",
        x0=-1,
        y0=0,
        x1=nlags+1,
        y1=0,
        line=dict(color="black", width=1)
    )
    
    fig.update_layout(
        title=f"Partial Autocorrelation (PACF)",
        xaxis_title="Lag",
        yaxis_title="PACF",
        hovermode="x",
        showlegend=True
    )
    
    visuals["pacf_plot"] = fig.to_json()
    
    return visuals