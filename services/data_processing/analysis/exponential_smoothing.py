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

    # Coerce empty strings to None (frontend may send '' instead of null)
    _trend = getattr(inputs, 'trend', None) or None
    _seasonal = getattr(inputs, 'seasonal', None) or None
    _seasonal_periods = getattr(inputs, 'seasonal_periods', None) or None
    _smoothing_level = getattr(inputs, 'smoothing_level', None) or None
    if _seasonal is not None and not _seasonal_periods:
        raise ValueError(
            "seasonal_periods must be specified when a seasonal model is requested. "
            "Example: seasonal_periods=12 for monthly data with yearly seasonality."
        )
    if _seasonal_periods and len(ts_data) < 2 * _seasonal_periods:
        raise ValueError(
            f"Insufficient data for seasonal model: need at least "
            f"{2 * _seasonal_periods} observations for seasonal_periods={_seasonal_periods}, "
            f"got {len(ts_data)}"
        )
    if _seasonal in ('mul', 'multiplicative') and (ts_data <= 0).any():
        raise ValueError(
            "Multiplicative seasonal model requires all values to be strictly positive (> 0)"
        )

    # Fit model
    try:
        model = ExponentialSmoothing(
            ts_data,
            trend=_trend,
            seasonal=_seasonal,
            seasonal_periods=_seasonal_periods,
            damped_trend=getattr(inputs, 'damped_trend', False)
        ).fit(smoothing_level=_smoothing_level)
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
            "trend": _trend,
            "seasonal": _seasonal,
            "seasonal_periods": _seasonal_periods,
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
            model_type="Holt-Winters" if _seasonal else "Holt's" if _trend else "Simple"
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


