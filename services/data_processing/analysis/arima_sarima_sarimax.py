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

    forecast = result.get_forecast(
        steps=inputs.order[0],
        exog=exog.iloc[-inputs.order[0]:] if exog is not None else None
    )

    # Serialize forecast DataFrame to JSON-safe format
    forecast_df = forecast.summary_frame()
    forecast_df = forecast_df.reset_index()
    forecast_df["index"] = forecast_df["index"].astype(str)
    forecast_dict = forecast_df.to_dict(orient="records")

    results = {
        "params": result.params.to_dict(),
        "aic": result.aic,
        "bic": result.bic,
        "forecast": forecast_dict
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
