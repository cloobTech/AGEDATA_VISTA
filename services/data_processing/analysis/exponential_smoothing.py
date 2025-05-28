from statsmodels.tsa.holtwinters import ExponentialSmoothing
from typing import Dict, Any
import pandas as pd
from schemas.data_processing import AnalysisInput
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.visualization.exponential_smoothing import generate_es_visualizations
from services.data_processing.report import crud


async def perform_exponential_smoothing(
    data: pd.DataFrame, 
    input: AnalysisInput, 
    session: AsyncSession
) -> Dict[str, Any]:
    """Perform exponential smoothing analysis"""
    inputs = input.analysis_input

    # Validate parameters
    if not hasattr(inputs, 'time_col') or not inputs.time_col:
        raise ValueError("Exponential smoothing requires time_col parameter")
    if not hasattr(inputs, 'value_col') or not inputs.value_col:
        raise ValueError("Exponential smoothing requires value_col parameter")

    # Prepare data
    ts_data = data.set_index(inputs.time_col)[inputs.value_col]
    
    # Fit model
    try:
        model = ExponentialSmoothing(
            ts_data,
            trend=getattr(inputs, 'trend', None),
            seasonal=getattr(inputs, 'seasonal', None),
            seasonal_periods=getattr(inputs, 'seasonal_periods', None),
            damped_trend=getattr(inputs, 'damped_trend', False)
        ).fit(smoothing_level=getattr(inputs, 'smoothing_level', None))
    except Exception as e:
        raise ValueError(f"Exponential smoothing failed: {str(e)}")

    # Get fitted values
    fitted = model.fittedvalues
    
    # Prepare results
    results = {
        "original": ts_data.to_dict(),
        "fitted": fitted.to_dict(),
        "parameters": {
            "smoothing_level": model.params["smoothing_level"],
            "trend": getattr(inputs, 'trend', None),
            "seasonal": getattr(inputs, 'seasonal', None),
            "seasonal_periods": getattr(inputs, 'seasonal_periods', None),
            "damped_trend": getattr(inputs, 'damped_trend', False)
        },
        "model_stats": {
            "AIC": model.aic,
            "BIC": model.bic,
            "SSE": model.sse
        }
    }

    visualizations = {}

    if input.generate_visualizations:
        visualizations = generate_es_visualizations(
            original=ts_data,
            fitted=fitted,
            model_type="Holt-Winters" if inputs.seasonal else "Holt's" if inputs.trend else "Simple"
        )

    # Create and store report
    report = await crud.create_report({
        "visualizations": visualizations,
        'project_id': input.project_id,
        'summary': results,
        'title': input.title,
        'analysis_group': input.analysis_group
    }, session=session)
    
    return report


