import plotly.graph_objects as go
import pandas as pd
import numpy as np


def generate_es_visualizations(
    original: pd.Series,
    fitted: pd.Series,
    model_type: str
) -> dict:
    """Generate professional exponential smoothing visualizations"""
    visuals = {}
    
    # Main smoothing plot
    fig = go.Figure()
    
    # Original series - professional styling
    fig.add_trace(go.Scatter(
        x=original.index,
        y=original,
        name="Original Series",
        line=dict(color='#1f77b4', width=2),  # Professional blue
        opacity=0.8,
        hovertemplate="Time: %{x}<br>Value: %{y:.3f}<extra></extra>"
    ))
    
    # Fitted values - professional styling
    fig.add_trace(go.Scatter(
        x=fitted.index,
        y=fitted,
        name=f"Fitted ({model_type})",
        line=dict(color='#2ca02c', width=3),  # Professional green
        opacity=0.9,
        hovertemplate="Time: %{x}<br>Fitted: %{y:.3f}<extra></extra>"
    ))
    
    # Calculate and display performance metrics
    residuals = original - fitted
    mse = np.mean(residuals**2)
    mae = np.mean(np.abs(residuals))
    
    fig.update_layout(
        title=dict(
            text=f"Exponential Smoothing Fit - {model_type}<br><sup>MSE: {mse:.3f} | MAE: {mae:.3f}</sup>",
            x=0.05,
            xanchor='left',
            font=dict(size=18, color='#2a3f5f')
        ),
        xaxis_title="Time",
        yaxis_title="Value",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            showline=True,
            linewidth=2,
            linecolor='#2a3f5f'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            showline=True,
            linewidth=2,
            linecolor='#2a3f5f'
        ),
        hovermode="x unified",
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=1000,
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#E5ECF6',
            borderwidth=1
        ),
        margin=dict(l=80, r=50, t=100, b=80)
    )
    
    visuals["smoothing_plot"] = fig.to_json()
    
    # Residuals plot with professional styling
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=residuals.index,
        y=residuals,
        mode='markers',
        name="Residuals",
        marker=dict(
            color='#ff7f0e',  # Professional orange
            size=6,
            opacity=0.7,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        hovertemplate="Time: %{x}<br>Residual: %{y:.3f}<extra></extra>"
    ))
    
    # Add zero reference line
    fig.add_hline(
        y=0, 
        line_dash="dash", 
        line_width=2, 
        line_color='#2a3f5f',
        annotation_text="Zero Reference", 
        annotation_position="top right",
        annotation_font_size=12
    )
    
    # Add confidence bands (2 standard deviations)
    residual_std = np.std(residuals)
    if np.isfinite(residual_std) and residual_std > 0:
        fig.add_hrect(
            y0=-2*residual_std,
            y1=2*residual_std,
            fillcolor="rgba(0, 0, 0, 0.1)",
            line_width=0,
            annotation_text="±2σ",
            annotation_position="bottom right"
        )
    
    fig.update_layout(
        title=dict(
            text=f"Residual Analysis - {model_type}<br><sup>Standard Deviation: {residual_std:.3f if np.isfinite(residual_std) else 'N/A'}</sup>",
            x=0.05,
            xanchor='left',
            font=dict(size=18, color='#2a3f5f')
        ),
        xaxis_title="Time",
        yaxis_title="Residual Value",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            showline=True,
            linewidth=2,
            linecolor='#2a3f5f'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            showline=True,
            linewidth=2,
            linecolor='#2a3f5f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=1000,
        height=500,
        showlegend=False,
        hovermode="x unified"
    )
    
    visuals["residuals_plot"] = fig.to_json()
    
    # Additional: Residual distribution plot
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=residuals,
        name="Residual Distribution",
        marker_color='#1f77b4',
        opacity=0.7,
        nbinsx=30,
        histnorm='probability density'
    ))
    
    # Add normal distribution overlay (only when std is valid)
    if np.isfinite(residual_std) and residual_std > 0:
        x_norm = np.linspace(residuals.min(), residuals.max(), 100)
        y_norm = (1/(residual_std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_norm - residuals.mean()) / residual_std) ** 2)
        fig.add_trace(go.Scatter(
            x=x_norm,
            y=y_norm,
            mode='lines',
            name='Normal Distribution',
            line=dict(color='red', width=2.5, dash='dash')
        ))
    
    fig.update_layout(
        title=dict(
            text=f"Residual Distribution - {model_type}",
            x=0.05,
            xanchor='left',
            font=dict(size=18, color='#2a3f5f')
        ),
        xaxis_title="Residual Value",
        yaxis_title="Density",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            showline=True,
            linewidth=2,
            linecolor='#2a3f5f'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            showline=True,
            linewidth=2,
            linecolor='#2a3f5f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=800,
        height=500,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    visuals["residual_distribution"] = fig.to_json()
    
    return visuals