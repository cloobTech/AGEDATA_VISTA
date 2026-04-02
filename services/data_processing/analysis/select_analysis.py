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
from services.data_processing.analysis.logistic_regression import perform_logistic_regression
from services.data_processing.analysis.tree_model import perform_tree_analysis
from services.data_processing.analysis.gradient_boosting import perform_gradient_boosting_analysis
from services.data_processing.analysis.svm import perform_svm_analysis
from services.data_processing.analysis.knn import perform_knn_analysis
from services.data_processing.analysis.neural_network import perform_neural_network_analysis
from services.data_processing.analysis.resampling import perform_resampling_analysis
from services.data_processing.analysis.imputation import perform_imputation_analysis

from schemas.data_processing import (
    AnalysisInput,
    DescriptiveAnalysisInput,
    RegressionInput,
    Anova,
    CorrelationAnalysisInput,
    PCAInput,
    ClusterAnalysisInput,
    CCAInput,
    TimeSeriesDecompsition,
    MovingAverageInput,
    ExponentialSmoothingInput,
    ACFPACFInput,
    ArimaInput,
    ForecastInput,
    LogisticRegressionInput,
    TreeModelInput,
    GradientBoostingInput,
    SVMInput,
    KNNInput,
    NeuralNetworkInput,
    ResamplingInput,
    ImputationInput,
)


# Maps analysis_type → (analysis function, expected input schema class)
_ANALYSIS_REGISTRY = {
    "descriptive":              (perform_descriptive_analysis,        DescriptiveAnalysisInput),
    "regression":               (perform_regression,                  RegressionInput),
    "anova":                    (perform_anova,                       Anova),
    "correlation_analysis":     (perform_correlation_analysis,        CorrelationAnalysisInput),
    "pca":                      (perform_pca_analysis,                PCAInput),
    "cluster":                  (perform_cluster_analysis,            ClusterAnalysisInput),
    "canonical_correlation":    (perform_cca_analysis,                CCAInput),
    "time_series_decomposition":(perform_time_series_decomposition,   TimeSeriesDecompsition),
    "moving_average":           (perform_moving_average,              MovingAverageInput),
    "exponential_smoothing":    (perform_exponential_smoothing,       ExponentialSmoothingInput),
    "acf_pacf":                 (perform_acf_pacf,                    ACFPACFInput),
    "arima_sarima_sarimax":     (perform_arima_analysis,              ArimaInput),
    "arima":                    (perform_arima_analysis,              ArimaInput),  # alias from Projects.jsx
    "forecast":                 (perform_forecasting,                 ForecastInput),
    "logistic_regression":      (perform_logistic_regression,         LogisticRegressionInput),
    "tree_model":               (perform_tree_analysis,               TreeModelInput),
    "gradient_boosting":        (perform_gradient_boosting_analysis,  GradientBoostingInput),
    "svm":                      (perform_svm_analysis,                SVMInput),
    "knn":                      (perform_knn_analysis,                KNNInput),
    "neural_network":           (perform_neural_network_analysis,     NeuralNetworkInput),
    "resampling":               (perform_resampling_analysis,         ResamplingInput),
    "imputation":               (perform_imputation_analysis,         ImputationInput),
}


def _parse_analysis_input(analysis_type: str, raw_input):
    """
    Parse the raw analysis_input (dict or already-typed object) to the correct
    Pydantic schema for the given analysis_type.

    This is necessary because AnalysisInput.analysis_input is typed as Any to
    avoid Pydantic's ambiguous Union matching (LogisticRegressionInput has the
    same required fields as SVMInput/KNNInput and would be matched first).
    """
    if analysis_type not in _ANALYSIS_REGISTRY:
        raise ValueError(
            f"Invalid analysis type '{analysis_type}'. "
            f"Must be one of: {sorted(_ANALYSIS_REGISTRY)}"
        )

    _, schema_cls = _ANALYSIS_REGISTRY[analysis_type]

    # Already correctly typed (e.g. called from tests directly)
    if isinstance(raw_input, schema_cls):
        return raw_input

    # Convert dict → typed schema
    if isinstance(raw_input, dict):
        try:
            return schema_cls(**raw_input)
        except Exception as exc:
            raise ValueError(
                f"Invalid analysis_input for '{analysis_type}' "
                f"({schema_cls.__name__}): {exc}"
            ) from exc

    # Unknown type — try schema coercion via model_validate
    try:
        return schema_cls.model_validate(raw_input)
    except Exception as exc:
        raise ValueError(
            f"Could not coerce analysis_input to {schema_cls.__name__}: {exc}"
        ) from exc


async def perform_analysis(
    df: pd.DataFrame | str,
    inputs: AnalysisInput,
    session: AsyncSession,
) -> dict:
    """
    Dispatch to the correct analysis function based on inputs.analysis_type.
    Parses inputs.analysis_input to the correct typed schema before dispatching.
    """
    if inputs.analysis_type not in _ANALYSIS_REGISTRY:
        raise ValueError(
            f"Invalid analysis type, must be one of: {sorted(_ANALYSIS_REGISTRY)}"
        )

    # Parse raw dict → correct typed sub-schema
    typed_input = _parse_analysis_input(inputs.analysis_type, inputs.analysis_input)

    # Replace the raw dict with the typed schema on the inputs object so that
    # analysis functions can safely do `inputs.analysis_input.feature_cols` etc.
    inputs = inputs.model_copy(update={"analysis_input": typed_input})

    analysis_fn, _ = _ANALYSIS_REGISTRY[inputs.analysis_type]
    return await analysis_fn(df, inputs, session)
