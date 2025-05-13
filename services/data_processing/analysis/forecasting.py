from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from typing import Dict, Any
from fastapi import HTTPException
import pandas as pd
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_progressing import SARIMAXConfig, ProphetConfig, ARIMAConfig, ForecastInput
from services.data_processing.report import crud
# from services.data_processing.visualization.forecasting import generate_forecast_visualizations
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet


from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def run_sarimax(
    data: pd.DataFrame,
    time_col: str,
    value_col: str,
    config: SARIMAXConfig,
    forecast_steps: int,
    exog_cols: Optional[List[str]] = None  # Only SARIMAX uses exogenous vars
) -> dict:
    """SARIMAX model implementation"""
    train = data.set_index(time_col)[value_col]
    exog = data.set_index(time_col)[exog_cols] if exog_cols else None

    model = SARIMAX(
        train,
        exog=exog,
        order=tuple(config.order),
        seasonal_order=tuple(
            config.seasonal_order) if config.seasonal_order else (0, 0, 0, 0),
        enforce_stationarity=config.enforce_stationarity,
        enforce_invertibility=config.enforce_invertibility
    ).fit(disp=False)

    forecast = model.get_forecast(
        steps=forecast_steps, exog=exog[-forecast_steps:] if exog_cols else None)

    return {
        "model": model,
        "forecast": forecast.predicted_mean,
        "conf_int": forecast.conf_int(),
        "metrics": {
            "aic": model.aic,
            "bic": model.bic
        }
    }


def run_prophet(
    data: pd.DataFrame,
    time_col: str,
    value_col: str,
    config: ProphetConfig,
    forecast_steps: int,
    **kwargs  # Accept but ignore other arguments
) -> dict:
    """Prophet model implementation"""
    # Remove the exog_cols from kwargs if present
    kwargs.pop('exog_cols', None)
    df = data.rename(columns={time_col: "ds", value_col: "y"})

    model = Prophet(
        seasonality_mode=config.seasonality_mode,
        yearly_seasonality=config.yearly_seasonality,
        weekly_seasonality=config.weekly_seasonality,
        daily_seasonality=config.daily_seasonality,
        changepoint_prior_scale=config.changepoint_prior_scale
    )

    if config.holidays:
        model.add_country_holidays(config.holidays)

    model.fit(df)

    future = model.make_future_dataframe(periods=forecast_steps)
    forecast = model.predict(future)

    return {
        "model": model,
        "forecast": forecast.set_index("ds")["yhat"],
        "conf_int": forecast.set_index("ds")[["yhat_lower", "yhat_upper"]],
        "components": model.plot_components(forecast)
    }

def run_arima(
    data: pd.DataFrame,
    time_col: str,
    value_col: str,
    config: ARIMAConfig,
    forecast_steps: int,
    **kwargs  # Accept but ignore other arguments
) -> dict:
    """ARIMA model implementation"""
    kwargs.pop('exog_cols', None)
    train = data.set_index(time_col)[value_col]

    model = ARIMA(
        train,
        order=tuple(config.order)
    ).fit()

    forecast = model.get_forecast(steps=forecast_steps)

    return {
        "model": model,
        "forecast": forecast.predicted_mean,
        "conf_int": forecast.conf_int(),
        "metrics": {
            "aic": model.aic,
            "bic": model.bic
        }
    }


async def perform_forecasting(
    data: pd.DataFrame,
    inputs: ForecastInput,
    session: AsyncSession
) -> Dict[str, Any]:
    input = inputs.analysis_input
    
    try:
        # Validate input
        if input.model_type == "sarimax" and not input.sarimax:
            raise HTTPException(400, "SARIMAX configuration required")
        if input.model_type == "prophet" and not input.prophet:
            print(input.prophet)
            raise HTTPException(400, "Prophet configuration required")
        if input.model_type == "arima" and not input.arima:
            raise HTTPException(400, "ARIMA configuration required")

        # Convert datetime if needed
        data[input.time_col] = pd.to_datetime(data[input.time_col])

        # Split train-test
        if input.test_size:
            test_size = int(len(data) * input.test_size)
            train_data = data.iloc[:-test_size]
            test_data = data.iloc[-test_size:]
        else:
            train_data = data

        # Select and run model
        model_funcs = {
            "sarimax": run_sarimax,
            "prophet": run_prophet,
            "arima": run_arima
        }

        model_config = {
            "sarimax": input.sarimax,
            "prophet": input.prophet,
            "arima": input.arima
        }[input.model_type]

        results = model_funcs[input.model_type](
            data=train_data,
            time_col=input.time_col,
            value_col=input.value_col,
            config=model_config,
            forecast_steps=input.forecast_steps,
            exog_cols=input.exog_cols
        )

        # Calculate metrics if test data exists
        metrics = {}
        if input.test_size:
            test_values = test_data.set_index(input.time_col)[input.value_col]
            metrics = {
                "mae": mean_absolute_error(test_values, results["forecast"][:len(test_values)]),
                "rmse": np.sqrt(mean_squared_error(test_values, results["forecast"][:len(test_values)]))
            }

        # Generate visualizations
        visualization = generate_forecast_visualizations(
            history=train_data.set_index(input.time_col)[input.value_col],
            forecast=results["forecast"],
            conf_int=results.get("conf_int"),
            test_data=test_data.set_index(input.time_col)[
                input.value_col] if input.test_size else None,
            model_name=input.model_type
        )

        # Add components plot for Prophet
        if input.model_type == "prophet":
            visualization["components_plot"] = prophet_components_to_json(
                results["components"])

        report = await crud.create_report({
            "visualizations": visualization,
            'project_id': input.project_id,
            "summary": {
                "model": input.model_type,
                "forecast": results["forecast"].to_dict(),
                "metrics": metrics,
                "model_metrics": results.get("metrics", {})
            },
            'title': input.title,
            'analysis_group': input.analysis_group
        }, session=session)

        return report

    except Exception as e:
        raise HTTPException(500, f"Forecasting failed: {str(e)}")


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
