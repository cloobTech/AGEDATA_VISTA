from typing import  Optional, List
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from schemas.data_progressing import SARIMAXConfig, ProphetConfig, ARIMAConfig
import pandas as pd



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

