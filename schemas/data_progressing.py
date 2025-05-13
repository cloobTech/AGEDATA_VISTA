from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
from enum import Enum
from schemas.descriptive_visualization import DescriptiveVisualizations


class RegressionInput(BaseModel):
    """Regression Input"""
    regression_type: str = "linear"
    features_col: list
    label_col: str


class DescriptiveAnalysisInput(BaseModel):
    """Descriptive Analysis Input"""
    visualization_list: list = []
    descriptive_visualizations: DescriptiveVisualizations = None


class Anova(BaseModel):
    """Anova Analysis Input"""
    factor_cols: List[str]  # Columns to be used as factors (categorical variables)
    value_col: str          # Column to be used as the dependent variable
    # Whether to include interaction terms
    include_interactions: Optional[bool] = False
    # Whether to compute effect sizes
    calculate_effect_sizes: Optional[bool] = False


class CorrelationAnalysisInput(BaseModel):
    """Correlation Analysis Input"""
    numeric_cols: List[str]  # Columns to be included in correlation analysis
    method: str = "pearson"  # Correlation method: 'pearson', 'kendall', or 'spearman'
    # Whether to compute p-values
    compute_p_values: Optional[bool] = False


class PCAInput(BaseModel):
    """PCA Analysis Input"""
    numeric_cols: List[str]  # Columns to use for PCA
    n_components: Optional[int] = None  # Number of components to keep
    scale_data: Optional[bool] = True  # Whether to scale data (recommended)
    # Optional color grouping variable
    color_col: Optional[str] = None
    # Optional variable for additional hover information
    hover_col: Optional[str] = None


class ClusterAnalysisInput(BaseModel):
    """Cluster Analysis Input"""
    numeric_cols: List[str]
    method: str = "kmeans"  # or "hierarchical"
    n_clusters: int = 3
    scale_data: Optional[bool] = True
    color_col: Optional[str] = None
    hover_col: Optional[str] = None
    linkage: Optional[str] = "ward"  # Used only for hierarchical clustering


class CCAInput(BaseModel):
    x_cols: List[str]
    y_cols: List[str]
    n_components: Optional[int] = 2
    scale_data: Optional[bool] = True


class TimeSeriesDecompsition(BaseModel):
    """Time Series Decomposition Input"""
    time_col: str            # Column containing timestamps
    value_col: str           # Column containing values to analyze
    period: int
    freq: Optional[str] = None  # Frequency string (e.g., 'D' for daily)
    model: str = "additive"  # 'additive' or 'multiplicative'
    # Whether to show observed component
    show_observed: Optional[bool] = True
    # Whether to show trend component
    show_trend: Optional[bool] = True
    # Whether to show seasonal component
    show_seasonal: Optional[bool] = True
    # Whether to show residual component
    show_resid: Optional[bool] = True


class MovingAverageInput(BaseModel):
    """Moving Average Input"""
    time_col: str            # Column containing timestamps or sequence numbers
    value_col: str           # Column containing values to analyze
    window_size: int         # Size of the moving window
    # Minimum number of observations in window
    min_periods: Optional[int] = None
    center: Optional[bool] = False     # Center the moving average
    # Type: 'simple', 'cumulative', 'weighted', 'exponential'
    ma_type: Optional[str] = "simple"


class ExponentialSmoothingInput(BaseModel):
    """Exponential Smoothing Input"""
    time_col: str            # Column containing timestamps or sequence numbers
    value_col: str           # Column containing values to analyze
    smoothing_level: Optional[float] = None  # Alpha parameter
    trend: Optional[str] = None       # 'add' or 'mul'
    seasonal: Optional[str] = None    # 'add' or 'mul'
    seasonal_periods: Optional[int] = None
    damped_trend: Optional[bool] = False


class ACFPACFInput(BaseModel):
    """Autocorrelation (ACF) and Partial Autocorrelation (PACF) Input"""
    time_col: str            # Column containing timestamps or sequence numbers
    value_col: str           # Column containing values to analyze
    nlags: Optional[int] = 40  # Number of lags to compute
    alpha: Optional[float] = 0.05  # Confidence level
    fft: Optional[bool] = True  # Use FFT for ACF
    method: Optional[str] = 'yw'  # PACF method ('yw', 'ols', 'ld')


class ArimaInput(BaseModel):
    time_col: str
    value_col: str
    exog_cols: Optional[List[str]] = None  # For SARIMAX
    order: List[int]  # ARIMA (p, d, q)
    seasonal_order: Optional[List[int]] = None  # SARIMA/SARIMAX (P, D, Q, s)
    enforce_stationarity: bool = True
    enforce_invertibility: bool = True


class SARIMAXConfig(BaseModel):
    order: List[int] = Field(..., description="ARIMA order: [p, d, q]")
    seasonal_order: Optional[List[int]] = Field(
        default=None, description="Seasonal order: [P, D, Q, s]")
    enforce_stationarity: bool = True
    enforce_invertibility: bool = True

class ProphetConfig(BaseModel):
    seasonality_mode: Optional[Literal["additive", "multiplicative"]] = "additive"
    yearly_seasonality: Optional[bool] = True
    weekly_seasonality: Optional[bool] = False
    daily_seasonality: Optional[bool] = False
    changepoint_prior_scale: Optional[float] = 0.05
    holidays: Optional[List[dict]] = None

class ARIMAConfig(BaseModel):
    order: List[int] = Field(..., description="ARIMA order: [p, d, q]")

class ForecastInput(BaseModel):
    time_col: str
    value_col: str
    exog_cols: Optional[List[str]] = None
    forecast_steps: int = Field(10, ge=1)
    model_type: Literal["sarimax", "prophet", "arima"]
    sarimax: Optional[SARIMAXConfig] = None
    prophet: Optional[ProphetConfig] = None
    arima: Optional[ARIMAConfig] = None
    test_size: Optional[float] = Field(None, ge=0, le=0.5)


class ForecastModelType(str, Enum):
    ARIMA = "arima"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    PROPHET = "prophet"
    LSTM = "lstm"


# Define a type alias for all possible analysis input types
AnalysisInputType = Union[
    RegressionInput,
    DescriptiveAnalysisInput,
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
    ForecastInput
]


class AnalysisInput(BaseModel):
    """Base Analysis Input"""
    analysis_group: str
    columns: list = []
    analysis_type: str
    generate_visualizations: bool = False
    analysis_input: AnalysisInputType  # Use the type alias here
    title: str = "Analysis Report"
    project_id: str
    file_id: str
