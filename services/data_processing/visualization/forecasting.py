from typing import Dict, Optional
import plotly.graph_objects as go
import base64
from io import BytesIO
import pandas as pd
import numpy as np


def generate_forecast_visualizations(
    history: pd.Series,
    forecast: pd.Series,
    conf_int: Optional[pd.DataFrame],
    test_data: Optional[pd.Series],
    model_name: str
) -> Dict[str, str]:
    """Generate professional interactive forecast plots"""
    fig = go.Figure()

    # Calculate performance metrics if test data is available
    metrics_text = ""
    if test_data is not None and len(test_data) > 0:
        # Align test data with forecast period
        common_index = test_data.index.intersection(forecast.index)
        if len(common_index) > 0:
            test_aligned = test_data.loc[common_index]
            forecast_aligned = forecast.loc[common_index]
            
            # Calculate metrics
            mse = np.mean((test_aligned - forecast_aligned) ** 2)
            mae = np.mean(np.abs(test_aligned - forecast_aligned))
            mape = np.mean(np.abs((test_aligned - forecast_aligned) / test_aligned)) * 100
            
            metrics_text = f"<br><sup>Test Metrics: MSE: {mse:.3f} | MAE: {mae:.3f} | MAPE: {mape:.2f}%</sup>"

    # Historical data - professional styling
    fig.add_trace(go.Scatter(
        x=history.index,
        y=history,
        name="Historical Data",
        line=dict(color='#1f77b4', width=2.5),  # Professional blue
        opacity=0.9,
        hovertemplate="Date: %{x}<br>Value: %{y:.3f}<extra></extra>"
    ))

    # Test data if available - professional styling
    if test_data is not None:
        fig.add_trace(go.Scatter(
            x=test_data.index,
            y=test_data,
            name="Actual (Test Period)",
            line=dict(color='#2ca02c', width=2.5),  # Professional green
            opacity=0.9,
            hovertemplate="Date: %{x}<br>Actual: %{y:.3f}<extra></extra>"
        ))

    # Forecast - professional styling
    fig.add_trace(go.Scatter(
        x=forecast.index,
        y=forecast,
        name=f"{model_name.upper()} Forecast",
        line=dict(color='#ff7f0e', width=3, dash='solid'),  # Professional orange
        opacity=0.9,
        hovertemplate="Date: %{x}<br>Forecast: %{y:.3f}<extra></extra>"
    ))

    # Confidence intervals with professional styling
    if conf_int is not None and not conf_int.empty:
        # Get confidence interval column names
        lower_col = conf_int.columns[0]
        upper_col = conf_int.columns[1] if len(conf_int.columns) > 1 else conf_int.columns[0]
        
        # Create filled confidence interval
        fig.add_trace(go.Scatter(
            x=forecast.index.tolist() + forecast.index.tolist()[::-1],
            y=conf_int[upper_col].tolist() + conf_int[lower_col].tolist()[::-1],
            fill='toself',
            fillcolor='rgba(255, 127, 14, 0.2)',  # Orange with transparency
            line=dict(color='rgba(255, 255, 255, 0)'),
            name="95% Confidence Interval",
            hoverinfo='skip',
            showlegend=True
        ))

    # Add vertical line to separate history from forecast
    if len(forecast) > 0:
        forecast_start = forecast.index[0]
        fig.add_vline(
            x=forecast_start, 
            line_width=2, 
            line_dash="dash", 
            line_color="#d62728",  # Professional red
            annotation_text="Forecast Start", 
            annotation_position="top right",
            annotation_font_size=12,
            annotation_bgcolor="rgba(255, 255, 255, 0.8)"
        )

    fig.update_layout(
        title=dict(
            text=f"{model_name.upper()} Forecast{metrics_text}",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="Date",
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
        width=1100,
        height=700,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#E5ECF6',
            borderwidth=1,
            font=dict(size=12)
        ),
        margin=dict(l=80, r=50, t=120, b=80)
    )

    # Add forecast period annotation
    if len(forecast) > 0:
        forecast_period = f"{forecast.index[0].strftime('%Y-%m-%d')} to {forecast.index[-1].strftime('%Y-%m-%d')}"
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0.98, y=0.02,
            text=f"Forecast Period: {forecast_period}",
            showarrow=False,
            font=dict(size=11, color="#666666"),
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#E5ECF6",
            borderwidth=1
        )

    return {"forecast_plot": fig.to_json()}


def prophet_components_to_json(mpl_figure):
    """Convert Prophet components plot to Plotly JSON with professional styling"""
    buf = BytesIO()
    mpl_figure.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    
    # Create a Plotly figure to display the matplotlib image professionally
    fig = go.Figure()
    
    # Add the matplotlib image as a layout image
    fig.update_layout(
        images=[dict(
            source=f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}",
            xref="paper", yref="paper",
            x=0, y=1,
            sizex=1, sizey=1,
            xanchor="left", yanchor="top",
            layer="below"
        )],
        title=dict(
            text="Prophet Model Components",
            x=0.05,
            xanchor='left',
            font=dict(size=18, color='#2a3f5f')
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=1000,
        height=800,
        margin=dict(l=80, r=50, t=100, b=80)
    )
    
    # Hide axes since we're displaying an image
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    
    return fig.to_json()


# Optional: Additional forecast evaluation visualization
def generate_forecast_evaluation_plot(
    test_data: pd.Series, 
    forecast: pd.Series, 
    model_name: str
) -> str:
    """Generate a professional forecast evaluation scatter plot"""
    if test_data is None or len(test_data) == 0:
        return None
        
    common_index = test_data.index.intersection(forecast.index)
    if len(common_index) == 0:
        return None
        
    test_aligned = test_data.loc[common_index]
    forecast_aligned = forecast.loc[common_index]
    
    fig = go.Figure()
    
    # Perfect forecast line
    max_val = max(test_aligned.max(), forecast_aligned.max())
    min_val = min(test_aligned.min(), forecast_aligned.min())
    
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        name='Perfect Forecast',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    # Actual vs Forecast points
    fig.add_trace(go.Scatter(
        x=test_aligned,
        y=forecast_aligned,
        mode='markers',
        name='Forecast vs Actual',
        marker=dict(
            color='#1f77b4',
            size=8,
            opacity=0.7,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        hovertemplate="Actual: %{x:.3f}<br>Forecast: %{y:.3f}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text=f"Forecast Accuracy - {model_name.upper()}",
            x=0.05,
            xanchor='left',
            font=dict(size=18, color='#2a3f5f')
        ),
        xaxis_title="Actual Values",
        yaxis_title="Forecast Values",
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=600,
        height=600,
        showlegend=True
    )
    
    return fig.to_json()