from typing import Dict, Optional
import plotly.graph_objects as go
import base64
from io import BytesIO
import pandas as pd





def generate_forecast_visualizations(
    history: pd.Series,
    forecast: pd.Series,
    conf_int: Optional[pd.DataFrame],
    test_data: Optional[pd.Series],
    model_name: str
) -> Dict[str, str]:
    """Generate interactive forecast plots"""
    fig = go.Figure()

    # Historical data
    fig.add_trace(go.Scatter(
        x=history.index,
        y=history,
        name="Historical",
        line=dict(color='blue'),
        opacity=0.7
    ))

    # Test data if available
    if test_data is not None:
        fig.add_trace(go.Scatter(
            x=test_data.index,
            y=test_data,
            name="Test Data",
            line=dict(color='green')
        ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast.index,
        y=forecast,
        name=f"{model_name.upper()} Forecast",
        line=dict(color='red', dash='dash')
    ))

    # Confidence intervals
    if conf_int is not None:
        fig.add_trace(go.Scatter(
            x=forecast.index,
            y=conf_int.iloc[:, 0],
            fill=None,
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=forecast.index,
            y=conf_int.iloc[:, 1],
            fill='tonexty',
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(255, 0, 0, 0.2)',
            name="95% Confidence"
        ))

    fig.update_layout(
        title=f"{model_name.upper()} Forecast",
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode="x unified",
        template="plotly_white"
    )

    return {"forecast_plot": fig.to_json()}


def prophet_components_to_json(mpl_figure):
    """Convert Prophet components plot to Plotly JSON"""
    buf = BytesIO()
    mpl_figure.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
