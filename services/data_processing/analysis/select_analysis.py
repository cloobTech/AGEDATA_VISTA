import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.analysis.descriptive import perform_descriptive_analysis
from services.data_processing.analysis.regression import perform_regression
from services.data_processing.analysis.anova import perform_anova
from services.data_processing.analysis.correlation_analysis import perform_correlation_analysis
from services.data_processing.analysis.pca import perform_pca_analysis
from services.data_processing.analysis.cluster_analysis import perform_cluster_analysis
from services.data_processing.analysis.canonical_correlation import perform_cca_analysis
from services.data_processing.analysis.time_series_decomposition import perform_time_series_decomposition
from services.data_processing.analysis.moving_average import perform_moving_average
from services.data_processing.analysis.exponential_smoothing import perform_exponential_smoothing
from services.data_processing.analysis.acf_pacf import perform_acf_pacf
from services.data_processing.analysis.arima_sarima_sarimax import perform_arima_analysis
from services.data_processing.analysis.forecasting import perform_forecasting

from schemas.data_progressing import (
    AnalysisInput, DescriptiveAnalysisInput, RegressionInput, Anova, CorrelationAnalysisInput, PCAInput, ClusterAnalysisInput, CCAInput, TimeSeriesDecompsition, MovingAverageInput, ExponentialSmoothingInput, ACFPACFInput, ArimaInput, ForecastInput)


anaylsis_functions = {
    "descriptive": perform_descriptive_analysis,
    "regression": perform_regression,
    "anova": perform_anova,
    "correlation_analysis": perform_correlation_analysis,
    "pca": perform_pca_analysis,
    "cluster": perform_cluster_analysis,
    "canonical_correlation": perform_cca_analysis,
    "time_series_decomposition": perform_time_series_decomposition,
    "moving_average": perform_moving_average,
    "exponential_smoothing": perform_exponential_smoothing,
    "acf_pacf": perform_acf_pacf,
    "arima_sarima_sarimax": perform_arima_analysis,
    "forecast": perform_forecasting
}


async def perform_analysis(df: pd.DataFrame, inputs: AnalysisInput, session: AsyncSession) -> dict:
    """
    Perform analysis based on the input parameters.
    """
    if inputs.analysis_type not in anaylsis_functions:
        raise ValueError(
            f"Invalid analysis type, must be one of: {list(anaylsis_functions.keys())}")

    analysis_function = anaylsis_functions[inputs.analysis_type]
    if inputs.analysis_type == "descriptive":
        if not isinstance(inputs.analysis_input, DescriptiveAnalysisInput):
            raise ValueError("Invalid analysis input for descriptive analysis")
        response = await analysis_function(df, inputs, session)
    elif inputs.analysis_type == "regression":
        if not isinstance(inputs.analysis_input, RegressionInput):
            raise ValueError("Invalid analysis input for regression")
        response = await analysis_function(df, inputs, session)
    elif inputs.analysis_type == "anova":
        if not isinstance(inputs.analysis_input, Anova):
            raise ValueError("Invalid analysis input for anova")
        response = await analysis_function(df, inputs, session)
    elif inputs.analysis_type == "correlation_analysis":
        if not isinstance(inputs.analysis_input, CorrelationAnalysisInput):
            raise ValueError("Invalid analysis input for correlation_analysis")
        response = await analysis_function(df, inputs, session)
    elif inputs.analysis_type == "pca":
        if not isinstance(inputs.analysis_input, PCAInput):
            raise ValueError("Invalid analysis input for PCA")
        response = await analysis_function(df, inputs, session)
    elif inputs.analysis_type == "cluster":
        if not isinstance(inputs.analysis_input, ClusterAnalysisInput):
            raise ValueError("Invalid analysis input for Cluster Analysis")
        response = await analysis_function(df, inputs, session)
    elif inputs.analysis_type == "canonical_correlation":
        if not isinstance(inputs.analysis_input, CCAInput):
            raise ValueError(
                "Invalid analysis input for Canonical Correlation Analysis")
        response = await analysis_function(df, inputs, session)
    elif inputs.analysis_type == "time_series_decomposition":
        if not isinstance(inputs.analysis_input, TimeSeriesDecompsition):
            raise ValueError(
                "Invalid analysis input for Time Series Decomposition Analysis")
        response = await analysis_function(df, inputs, session)
    elif inputs.analysis_type == "moving_average":
        if not isinstance(inputs.analysis_input, MovingAverageInput):
            raise ValueError(
                "Invalid analysis input for Moving average Analysis")
        response = await analysis_function(df, inputs, session)
    elif inputs.analysis_type == "exponential_smoothing":
        if not isinstance(inputs.analysis_input, ExponentialSmoothingInput):
            raise ValueError(
                "Invalid analysis input for Exponential Smoothing Analysis")
        response = await analysis_function(df, inputs, session)
    elif inputs.analysis_type == "acf_pacf":
        if not isinstance(inputs.analysis_input, ACFPACFInput):
            raise ValueError(
                "Invalid analysis input for Autocorrelation (ACF) and Partial Autocorrelation (PACF) Analysis")
        response = await analysis_function(df, inputs, session)
    elif inputs.analysis_type == "arima_sarima_sarimax":
        if not isinstance(inputs.analysis_input, ArimaInput):
            raise ValueError(
                "Invalid analysis input for ARIMA/SARIMA/SARIMAX Analysis")
        response = await analysis_function(df, inputs, session)
    elif inputs.analysis_type == "forecast":
        if not isinstance(inputs.analysis_input, ForecastInput):
            raise ValueError(
                "Invalid analysis input for Forecast Analysis")
        response = await analysis_function(df, inputs, session)
    return response
