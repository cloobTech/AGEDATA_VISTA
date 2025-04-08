import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.analysis.descriptive import perform_descriptive_analysis
from services.data_processing.analysis.regression import perform_regression
from schemas.data_progressing import AnalysisInput, DescriptiveAnalysisInput, RegressionInput


anaylsis_functions = {
    "descriptive_analysis": perform_descriptive_analysis,
    "regression": perform_regression
}


async def perform_analysis(df: pd.DataFrame, inputs: AnalysisInput, session: AsyncSession) -> dict:
    """
    Perform analysis based on the input parameters.
    """
    if inputs.analysis_type not in anaylsis_functions:
        raise ValueError(
            f"Invalid analysis type, must be one of: {list(anaylsis_functions.keys())}")

    analysis_function = anaylsis_functions[inputs.analysis_type]
    if inputs.analysis_type == "descriptive_analysis":
        if not isinstance(inputs.analysis_input, DescriptiveAnalysisInput):
            raise ValueError("Invalid analysis input for descriptive analysis")
        response = await analysis_function(df, inputs.analysis_input, session)
    elif inputs.analysis_type == "regression":
        if not isinstance(inputs.analysis_input, RegressionInput):
            raise ValueError("Invalid analysis input for regression")
        response = await analysis_function(df, inputs.analysis_input, session)

    return response
