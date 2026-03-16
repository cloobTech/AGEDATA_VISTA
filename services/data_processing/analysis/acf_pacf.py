from statsmodels.tsa.stattools import acf, pacf
from typing import Dict, Any
import pandas as pd
from schemas.data_processing import AnalysisInput
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.visualization.acf_pacf import generate_acf_pacf_visualizations
from services.data_processing.report import crud


async def perform_acf_pacf(
    data: pd.DataFrame, 
    input: AnalysisInput, 
    session: AsyncSession
) -> Dict[str, Any]:
    """Perform Autocorrelation (ACF) and Partial Autocorrelation (PACF) analysis"""
    inputs = input.analysis_input

    # Validate parameters
    if not hasattr(inputs, 'time_col') or not inputs.time_col:
        raise ValueError("ACF/PACF requires time_col parameter")
    if not hasattr(inputs, 'value_col') or not inputs.value_col:
        raise ValueError("ACF/PACF requires value_col parameter")

    # Prepare data
    ts_data = data.set_index(inputs.time_col)[inputs.value_col].dropna()

    if len(ts_data) < 2:
        raise ValueError("Insufficient data points for ACF/PACF analysis")

    # Clamp nlags to statsmodels requirement: nlags <= nobs//2 - 1
    max_nlags = max(1, len(ts_data) // 2 - 1)
    nlags = min(inputs.nlags if inputs.nlags and inputs.nlags > 0 else 40, max_nlags)

    # Clamp alpha to valid open interval (0, 1)
    alpha = inputs.alpha if inputs.alpha and 0 < inputs.alpha < 1 else 0.05

    # Calculate ACF
    acf_values, acf_confint = acf(
        ts_data,
        nlags=nlags,
        alpha=alpha,
        fft=inputs.fft
    )

    # Calculate PACF
    pacf_values, pacf_confint = pacf(
        ts_data,
        nlags=nlags,
        alpha=alpha,
        method=inputs.method
    )

    # Prepare results
    results = {
        "acf": {
            "values": acf_values.tolist(),
            "confidence_intervals": acf_confint.tolist()
        },
        "pacf": {
            "values": pacf_values.tolist(),
            "confidence_intervals": pacf_confint.tolist()
        },
        "parameters": {
            "nlags": nlags,
            "alpha": alpha,
            "fft": inputs.fft,
            "method": inputs.method
        }
    }

    visualizations = {}

    if input.generate_visualizations:
        visualizations = generate_acf_pacf_visualizations(
            acf_values=acf_values,
            pacf_values=pacf_values,
            acf_confint=acf_confint,
            pacf_confint=pacf_confint,
            nlags=nlags,
            alpha=alpha
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


