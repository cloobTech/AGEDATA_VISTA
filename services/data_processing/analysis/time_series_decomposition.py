from statsmodels.tsa.seasonal import seasonal_decompose
from typing import Dict, Any
import pandas as pd
import numpy as np
from services.data_processing.report import crud
from services.data_processing.visualization.time_series_decomposition import generate_decomposition_visualizations
from schemas.data_processing import AnalysisInput
from sqlalchemy.ext.asyncio import AsyncSession


async def perform_time_series_decomposition(
    data: pd.DataFrame,
    input: AnalysisInput,
    session: AsyncSession
) -> Dict[str, Any]:
    inputs = input.analysis_input

    if not hasattr(inputs, 'time_col') or not inputs.time_col:
        raise ValueError(
            "Time series decomposition requires time_col parameter")
    if not hasattr(inputs, 'value_col') or not inputs.value_col:
        raise ValueError(
            "Time series decomposition requires value_col parameter")

    # Convert time column to datetime
    data[inputs.time_col] = pd.to_datetime(data[inputs.time_col])

    # Prepare and sort data
    data = data.sort_values(by=inputs.time_col)
    ts_data = data.set_index(inputs.time_col)[inputs.value_col]

    # Ensure datetime index has frequency
    inferred_freq = ts_data.index.inferred_freq
    if inferred_freq is None:
        ts_data = ts_data.asfreq('D')  # Default to daily if unknown
    else:
        ts_data = ts_data.asfreq(inferred_freq)

    # Determine period
    period = getattr(inputs, 'period', None)
    if period is None:
        raise ValueError(
            "You must specify a period for decomposition (e.g., 12 for monthly data)")

    if len(ts_data) < 2 * period:
        raise ValueError(
            f"Time series too short: seasonal_decompose requires at least "
            f"{2 * period} data points for period={period}, got {len(ts_data)}"
        )
    if inputs.model == 'multiplicative' and (ts_data <= 0).any():
        raise ValueError(
            "Multiplicative decomposition requires all values to be strictly positive (> 0). "
            "Use model='additive' for data with zero or negative values."
        )

    # Perform decomposition
    try:
        decomposition = seasonal_decompose(
            ts_data,
            model=inputs.model,
            period=period,
            filt=None,
            two_sided=True,
            extrapolate_trend=0
        )
    except Exception as e:
        raise ValueError(f"Decomposition failed: {str(e)}")

    # Prepare results
    results = {
        "model": inputs.model,
        "components": {
            "observed": {str(k): v for k, v in decomposition.observed.items()},
            "trend": {str(k): v for k, v in decomposition.trend.items()},
            "seasonal": {str(k): v for k, v in decomposition.seasonal.items()},
            "resid": {str(k): v for k, v in decomposition.resid.items()},
        },

        "stats": {
            "residual_mean": float(np.nanmean(decomposition.resid)),
            "residual_std": float(np.nanstd(decomposition.resid)),
            "seasonal_amplitude": float(
                decomposition.seasonal.max() - decomposition.seasonal.min()
            )
        }
    }

    visualizations = {}
    if input.generate_visualizations:
        visualizations = generate_decomposition_visualizations(
            decomposition=decomposition,
            model_type=inputs.model,
            show_observed=getattr(inputs, 'show_observed', True),
            show_trend=getattr(inputs, 'show_trend', True),
            show_seasonal=getattr(inputs, 'show_seasonal', True),
            show_resid=getattr(inputs, 'show_resid', True)
        )

    report_obj = {
        "visualizations": visualizations,
        'project_id': input.project_id,
        'summary': results,
        'title': input.title,
        'analysis_group': input.analysis_group
    }

    report = await crud.create_report(report_obj, session=session)
    return report
