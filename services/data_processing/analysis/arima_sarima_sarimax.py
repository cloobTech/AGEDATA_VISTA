from statsmodels.tsa.statespace.sarimax import SARIMAX
import pandas as pd
from typing import Dict, Any
from schemas.data_processing import AnalysisInput
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.report import crud
from services.data_processing.visualization.arima_sarima_sarimax import generate_arima_visualizations


async def perform_arima_analysis(
    data: pd.DataFrame,
    input: AnalysisInput,
    session: AsyncSession
) -> Dict[str, Any]:
    inputs = input.analysis_input

    if not inputs.time_col or not inputs.value_col:
        raise ValueError("Both 'time_col' and 'value_col' must be specified.")

    df = data.copy()
    df[inputs.time_col] = pd.to_datetime(df[inputs.time_col])
    df.set_index(inputs.time_col, inplace=True)

    endog = df[inputs.value_col]
    exog = df[inputs.exog_cols] if inputs.exog_cols else None

    model = SARIMAX(
        endog=endog,
        exog=exog,
        order=tuple(inputs.order),
        seasonal_order=tuple(inputs.seasonal_order) if inputs.seasonal_order else (0, 0, 0, 0),
        enforce_stationarity=inputs.enforce_stationarity,
        enforce_invertibility=inputs.enforce_invertibility
    )

    result = model.fit(disp=False)

    _raw_steps = getattr(inputs, 'forecast_steps', 12)
    try:
        forecast_steps = int(_raw_steps)
    except (TypeError, ValueError):
        forecast_steps = 12
    if forecast_steps < 1:
        forecast_steps = 12
    forecast = result.get_forecast(
        steps=forecast_steps,
        exog=exog.iloc[-forecast_steps:] if exog is not None else None
    )

    # Serialize forecast DataFrame to JSON-safe format
    forecast_df = forecast.summary_frame()
    forecast_df = forecast_df.reset_index()
    forecast_df["index"] = forecast_df["index"].astype(str)
    forecast_dict = forecast_df.to_dict(orient="records")

    # Phase 5M: residual diagnostics — Ljung-Box, Shapiro-Wilk, Durbin-Watson
    residual_diagnostics = {}
    try:
        from statsmodels.stats.stattools import durbin_watson
        from statsmodels.stats.diagnostic import acorr_ljungbox
        from scipy.stats import shapiro as _shapiro

        residuals = result.resid.dropna()
        n_resid = len(residuals)

        lb_lags = [lag for lag in [10, 20] if lag < n_resid]
        if lb_lags:
            lb_test = acorr_ljungbox(residuals, lags=lb_lags, return_df=True)
            lb_results = {
                f"lag_{int(lag)}": {
                    "statistic": float(lb_test.loc[lag, "lb_stat"]),
                    "p_value":   float(lb_test.loc[lag, "lb_pvalue"]),
                }
                for lag in lb_lags
            }
            min_lb_p = float(lb_test["lb_pvalue"].min())
        else:
            lb_results = {}
            min_lb_p = 1.0

        sw_stat, sw_p = _shapiro(residuals.values[:min(n_resid, 5000)])
        dw = float(durbin_watson(residuals))

        residual_diagnostics = {
            "ljung_box":   lb_results,
            "shapiro_wilk_p": float(sw_p),
            "durbin_watson": dw,
            "white_noise": bool(min_lb_p > 0.05),
            "interpretation": (
                "Residuals appear as white noise (Ljung-Box p > 0.05 for all tested lags)."
                if min_lb_p > 0.05
                else "WARNING: Residual autocorrelation detected. Model may be misspecified."
            ),
        }
    except Exception as diag_exc:
        residual_diagnostics = {"error": str(diag_exc)}

    results = {
        "params": result.params.to_dict(),
        "aic": float(result.aic),
        "bic": float(result.bic),
        "forecast": forecast_dict,
        "residual_diagnostics": residual_diagnostics,
    }

    visualizations = {}
    if input.generate_visualizations:
        visualizations = generate_arima_visualizations(
            df=endog,
            result=result,
            forecast=forecast
        )

    report = await crud.create_report({
        "visualizations": visualizations,
        'project_id': input.project_id,
        'summary': results,
        'title': input.title,
        'analysis_group': input.analysis_group
    }, session=session)

    return report
