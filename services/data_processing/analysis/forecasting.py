from typing import Dict, Any
from fastapi import HTTPException
import pandas as pd
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_progressing import ForecastInput
from services.data_processing.report import crud
from services.data_processing.analysis.forecast_models import run_sarimax, run_prophet, run_arima
from services.data_processing.visualization.forecasting import generate_forecast_visualizations, prophet_components_to_json
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


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
            raise HTTPException(400, "Prophet configuration required")
        if input.model_type == "arima" and not input.arima:
            raise HTTPException(400, "ARIMA configuration required")

        # Convert datetime if needed
        if input.time_col in data.columns:
            data[input.time_col] = pd.to_datetime(data[input.time_col])
        else:
            data.index = pd.to_datetime(data.index)
            data.reset_index(inplace=True)

        # Split train-test
        if input.test_size:
            test_size = int(len(data) * input.test_size)
            train_data = data.iloc[:-test_size]
            test_data = data.iloc[-test_size:]
        else:
            train_data = data
            test_data = None

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

        # Convert forecast index (if it contains Timestamps) to strings
        forecast_dict = {
            str(k): v for k, v in results["forecast"].to_dict().items()}

        # Calculate metrics if test data exists
        metrics = {}
        if input.test_size:
            test_values = test_data.set_index(input.time_col)[input.value_col]
            forecast_values = results["forecast"][:len(test_values)]

            # Align test values with forecast values
            if len(test_values) > len(forecast_values):
                test_values = test_values[:len(forecast_values)]

            metrics = {
                "mae": mean_absolute_error(test_values, forecast_values),
                "rmse": np.sqrt(mean_squared_error(test_values, forecast_values))
            }

        # Generate visualizations
        if inputs.generate_visualizations:
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
            'project_id': inputs.project_id,
            "visualizations": visualization,
            "summary": {
                "model": input.model_type,
                "forecast": forecast_dict,
                "metrics": metrics,
                "model_metrics": results.get("metrics", {})
            },
            'title': inputs.title,
            'analysis_group': inputs.analysis_group
        }, session=session)

        return report

    except Exception as e:
        raise HTTPException(500, f"Forecasting failed: {str(e)}")
