import plotly.graph_objs as go
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAXResults
from typing import Dict, Any


def generate_arima_visualizations(df: pd.Series, result: SARIMAXResults, forecast) -> Dict[str, Any]:
    forecast_df = forecast.summary_frame()
    fitted = result.fittedvalues

    fig = go.Figure()
    
    # Observed data - thicker line for better visibility
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df.values, 
        name="Observed", 
        mode="lines",
        line=dict(width=2, color='#1f77b4'),  # Professional blue
        opacity=0.9
    ))
    
    # Fitted values
    fig.add_trace(go.Scatter(
        x=fitted.index, 
        y=fitted.values, 
        name="Fitted", 
        mode="lines", 
        line=dict(width=2.5, color='#2ca02c'),  # Professional green
        opacity=0.8
    ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_df.index, 
        y=forecast_df["mean"], 
        name="Forecast", 
        mode="lines", 
        line=dict(width=3, color='#ff7f0e'),  # Professional orange
        opacity=0.9
    ))
    
    # Confidence interval - lower bound
    fig.add_trace(go.Scatter(
        x=forecast_df.index, 
        y=forecast_df["mean_ci_lower"], 
        name="95% CI Lower", 
        mode="lines", 
        line=dict(dash='dot', width=1.5, color='#7f7f7f'),  # Professional gray
        opacity=0.7,
        showlegend=False
    ))
    
    # Confidence interval - upper bound
    fig.add_trace(go.Scatter(
        x=forecast_df.index, 
        y=forecast_df["mean_ci_upper"], 
        name="95% CI Upper", 
        mode="lines", 
        line=dict(dash='dot', width=1.5, color='#7f7f7f'),  # Professional gray
        opacity=0.7,
        showlegend=False
    ))
    
    # Confidence interval fill (creates the shaded area)
    fig.add_trace(go.Scatter(
        x=forecast_df.index.tolist() + forecast_df.index.tolist()[::-1],  # x, then x reversed
        y=forecast_df["mean_ci_upper"].tolist() + forecast_df["mean_ci_lower"].tolist()[::-1],  # upper, then lower reversed
        fill='toself',
        fillcolor='rgba(127, 127, 127, 0.2)',  # Light gray fill
        line=dict(color='rgba(255, 255, 255, 0)'),
        name='95% Confidence Interval',
        hoverinfo='skip'
    ))

    fig.update_layout(
        title=dict(
            text="ARIMA/SARIMA Forecast with Confidence Intervals", 
            x=0.05, 
            xanchor='left',
            font=dict(size=18)
        ),
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode="x unified",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#E5ECF6',
            borderwidth=1
        ),
        showlegend=True,
        plot_bgcolor='white',
        width=1000,
        height=600
    )

    # Add vertical line to separate historical data from forecast
    if len(forecast_df) > 0:
        forecast_start = forecast_df.index[0]
        fig.add_vline(
            x=forecast_start, 
            line_width=2, 
            line_dash="dash", 
            line_color="red",
            annotation_text="Forecast Start", 
            annotation_position="top right",
            annotation_font_size=12,
            annotation_bgcolor="rgba(255, 255, 255, 0.8)"
        )

    return {"forecast_plot": fig.to_json()}