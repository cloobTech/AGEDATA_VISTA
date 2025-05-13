from typing import Dict, Any
import pandas as pd
from schemas.data_progressing import AnalysisInput
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.visualization.moving_average import generate_ma_visualizations
from services.data_processing.report import crud


async def perform_moving_average(
    data: pd.DataFrame, 
    input: AnalysisInput, 
    session: AsyncSession
) -> Dict[str, Any]:
    """Perform moving average analysis"""
    inputs = input.analysis_input

    # Validate parameters
    if not hasattr(inputs, 'time_col') or not inputs.time_col:
        raise ValueError("Moving average requires time_col parameter")
    if not hasattr(inputs, 'value_col') or not inputs.value_col:
        raise ValueError("Moving average requires value_col parameter")
    if not hasattr(inputs, 'window_size') or inputs.window_size < 1:
        raise ValueError("window_size must be positive integer")

    # Prepare data
    ts_data = data.set_index(inputs.time_col)[inputs.value_col]
    
    # Calculate moving average
    if inputs.ma_type == "simple":
        ma = ts_data.rolling(
            window=inputs.window_size,
            min_periods=getattr(inputs, 'min_periods', inputs.window_size),
            center=getattr(inputs, 'center', False)
        ).mean()
    elif inputs.ma_type == "cumulative":
        ma = ts_data.expanding(min_periods=1).mean()
    elif inputs.ma_type == "weighted":
        ma = ts_data.rolling(
            window=inputs.window_size,
            min_periods=getattr(inputs, 'min_periods', inputs.window_size)
        ).mean()  # Simple weighted (equal weights)
    elif inputs.ma_type == "exponential":
        ma = ts_data.ewm(
            span=inputs.window_size,
            adjust=False
        ).mean()
    else:
        raise ValueError(f"Unknown moving average type: {inputs.ma_type}")

    # Prepare results
    results = {
        "original": ts_data.to_dict(),
        "moving_average": ma.to_dict(),
        "parameters": {
            "window_size": inputs.window_size,
            "ma_type": inputs.ma_type,
            "min_periods": getattr(inputs, 'min_periods', inputs.window_size),
            "center": getattr(inputs, 'center', False)
        }
    }

    visualizations = {}

    if input.generate_visualizations:
        visualizations = generate_ma_visualizations(
            original=ts_data,
            moving_avg=ma,
            ma_type=inputs.ma_type,
            window_size=inputs.window_size
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


