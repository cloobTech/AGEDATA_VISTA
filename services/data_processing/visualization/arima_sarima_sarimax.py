import plotly.graph_objs as go
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAXResults
from typing import Dict, Any


def generate_arima_visualizations(df: pd.Series, result: SARIMAXResults, forecast) -> Dict[str, Any]:
    forecast_df = forecast.summary_frame()
    fitted = result.fittedvalues

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df.values, name="Observed", mode="lines"))
    fig.add_trace(go.Scatter(x=fitted.index, y=fitted.values, name="Fitted", mode="lines", line=dict(color='green')))
    fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df["mean"], name="Forecast", mode="lines", line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df["mean_ci_lower"], name="Lower CI", mode="lines", line=dict(dash='dot', color='gray')))
    fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df["mean_ci_upper"], name="Upper CI", mode="lines", line=dict(dash='dot', color='gray')))

    fig.update_layout(title="ARIMA/SARIMA/SARIMAX Forecast", xaxis_title="Date", yaxis_title="Value")

    return {"forecast_plot": fig.to_json()}
