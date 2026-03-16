from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import List, Optional, Literal, Union, Tuple, Dict, Any
from schemas.descriptive_visualization import DescriptiveVisualizations


class RegressionInput(BaseModel):
    """Regression Input"""
    regression_type: str = "linear"
    features_col: list
    label_col: str


class DescriptiveAnalysisInput(BaseModel):
    """Descriptive Analysis Input"""
    visualization_list: list = []
    descriptive_visualizations: DescriptiveVisualizations | None = None


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
    forecast_steps: int = 12  # Number of periods to forecast


class SARIMAXConfig(BaseModel):
    order: List[int] = Field(..., description="ARIMA order: [p, d, q]")
    seasonal_order: Optional[List[int]] = Field(
        default=None, description="Seasonal order: [P, D, Q, s]")
    enforce_stationarity: bool = True
    enforce_invertibility: bool = True


class ProphetConfig(BaseModel):
    seasonality_mode: Optional[Literal["additive",
                                       "multiplicative"]] = "additive"
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


class LogisticRegressionInput(BaseModel):
    feature_cols: List[str]
    target_col: str
    test_size: float = Field(0.2, ge=0.1, le=0.5)
    penalty: Literal["l2", "none"] = "l2"
    solver: Literal["lbfgs", "liblinear", "sag", "saga", "newton-cg"] = "lbfgs"
    max_iter: int = 100
    multi_class: Literal["ovr", "ovo"] = "ovr"


class TreeModelType(str, Enum):
    DECISION_TREE = "decision_tree"
    RANDOM_FOREST = "random_forest"


class TreeModelConfig(BaseModel):
    # Common parameters
    max_depth: Optional[int] = Field(None, gt=0)
    min_samples_split: int = Field(2, gt=1)
    min_samples_leaf: int = Field(1, gt=0)
    criterion: Literal["gini", "entropy", "log_loss"] = "gini"
    random_state: Optional[int] = None

    # Random Forest specific
    n_estimators: int = Field(100, gt=0)  # Only for Random Forest
    max_features: Optional[str] = Field("sqrt")  # Only for Random Forest


class TreeModelInput(BaseModel):
    feature_cols: List[str]
    target_col: str
    model_type: TreeModelType
    config: TreeModelConfig
    test_size: float = Field(0.2, ge=0.1, le=0.5)
    task_type: Literal["classification", "regression"]


class GradientBoostingType(str, Enum):
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"


class GradientBoostingConfig(BaseModel):
    # Common parameters
    n_estimators: int = Field(100, gt=0)
    learning_rate: float = Field(0.1, gt=0)
    max_depth: int = Field(3, gt=0)
    subsample: float = Field(1.0, gt=0, le=1)
    random_state: Optional[int] = None

    # XGBoost specific
    gamma: float = Field(0, ge=0)  # Only for XGBoost
    reg_alpha: float = Field(0, ge=0)  # L1 regularization (XGBoost)
    reg_lambda: float = Field(1, ge=0)  # L2 regularization (XGBoost)

    # LightGBM specific
    num_leaves: int = Field(31, gt=1)  # Only for LightGBM
    min_child_samples: int = Field(20, ge=0)  # Only for LightGBM


class GradientBoostingInput(BaseModel):
    feature_cols: List[str]
    target_col: str
    model_type: GradientBoostingType
    config: GradientBoostingConfig
    test_size: float = Field(0.2, ge=0.1, le=0.5)
    task_type: Literal["classification", "regression"] = "classification"


class SVMKernel(str, Enum):
    LINEAR = "linear"
    POLY = "poly"
    RBF = "rbf"
    SIGMOID = "sigmoid"


class SVMConfig(BaseModel):
    C: float = Field(1.0, description="Regularization parameter")
    kernel: SVMKernel = Field(SVMKernel.RBF, description="Kernel type")
    degree: int = Field(3, description="Degree for polynomial kernel")
    gamma: Optional[str] = Field("scale", description="Kernel coefficient")
    probability: bool = Field(True, description="Enable probability estimates")
    random_state: Optional[int] = Field(None, description="Random seed")


class SVMInput(BaseModel):
    feature_cols: List[str]
    target_col: str
    test_size: float = Field(0.2, ge=0.1, le=0.5)
    config: SVMConfig
    task_type: Literal["classification", "regression"]


class KNNWeights(str, Enum):
    UNIFORM = "uniform"
    DISTANCE = "distance"


class KNNAlgorithm(str, Enum):
    AUTO = "auto"
    BALL_TREE = "ball_tree"
    KD_TREE = "kd_tree"
    BRUTE = "brute"


class KNNConfig(BaseModel):
    n_neighbors: int = Field(5, ge=1, description="Number of neighbors")
    weights: KNNWeights = Field(
        KNNWeights.UNIFORM, description="Weight function")
    algorithm: KNNAlgorithm = Field(
        KNNAlgorithm.AUTO, description="Algorithm used")
    p: int = Field(
        2, ge=1, description="Power parameter for Minkowski distance")
    metric: str = Field("minkowski", description="Distance metric")


class KNNInput(BaseModel):
    feature_cols: List[str]
    target_col: str
    test_size: float = Field(0.2, ge=0.1, le=0.5)
    config: KNNConfig
    task_type: Literal["classification", "regression"]


class ActivationFunction(str, Enum):
    RELU = "relu"
    SIGMOID = "sigmoid"
    TANH = "tanh"
    SOFTMAX = "softmax"


class OptimizerType(str, Enum):
    ADAM = "adam"
    SGD = "sgd"
    RMSprop = "rmsprop"


class DataType(str, Enum):
    TABULAR = "tabular"
    IMAGE = "image"


class NeuralNetworkConfig(BaseModel):
    image_size: Optional[Tuple[int, int]] = (256, 256)
    data_type: DataType = Field(
        DataType.TABULAR, description="Train Image or Tabular types"
    )
    hidden_layers: List[int] = Field(
        [64, 32], description="Number of neurons in each hidden layer")
    activation: ActivationFunction = Field(
        ActivationFunction.RELU, description="Activation function")
    optimizer: OptimizerType = Field(
        OptimizerType.ADAM, description="Optimization algorithm")
    learning_rate: float = Field(0.001, description="Learning rate")
    epochs: int = Field(50, description="Number of training epochs")
    batch_size: int = Field(32, description="Batch size")
    dropout_rate: Optional[float] = Field(
        None, ge=0, le=0.5, description="Dropout rate")
    early_stopping: bool = Field(True, description="Enable early stopping")
    validation_split: float = Field(
        0.1, ge=0.05, le=0.3, description="Validation split ratio")
    task_type: Literal["classification", "regression"]
    test_size: float = Field(0.2, ge=0.1, le=0.5)
    # Image-specific parameters
    data_path: Optional[str] = None  # Required for image data
    image_size: Optional[tuple] = (224, 224)  # Default image size


class NeuralNetworkInput(BaseModel):
    feature_cols: List[str]
    target_col: str
    test_size: float = Field(0.2, ge=0.1, le=0.5)
    config: NeuralNetworkConfig
    task_type: Literal["classification", "regression"]


# Define a type alias for all possible analysis input types
AnalysisInputType = Union[
    RegressionInput,
    LogisticRegressionInput,
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
    ForecastInput,
    TreeModelInput,
    GradientBoostingInput,
    SVMInput,
    KNNInput,
    NeuralNetworkInput
]


class AnalysisInput(BaseModel):
    """Base Analysis Input"""
    analysis_group: str
    columns: list = []
    analysis_type: str
    generate_visualizations: bool = False
    # Accept the sub-schema as a raw dict; select_analysis.py parses it to the
    # correct typed schema based on analysis_type (avoids Pydantic union ambiguity
    # where LogisticRegressionInput would match before SVMInput/KNNInput).
    analysis_input: Any
    title: str = "Analysis Report"
    project_id: str
    file_id: str


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DataSourceType(str, Enum):
    FILE = "file"
    DATABASE = "database"
    HIVE = "hive"
    KAFKA = "kafka"
    URL = "url"
    CLOUD = "cloud"
    HDFS = "hdfs"


class FileFormat(str, Enum):
    PARQUET = "parquet"
    CSV = "csv"
    JSON = "json"
    ORC = "orc"
    AVRO = "avro"
    EXCEL = "excel"


class SourceConfig(BaseModel):
    type: DataSourceType
    path: Optional[str] = None
    url: Optional[str] = None
    format: Optional[FileFormat] = None
    table: Optional[str] = None
    table_name: Optional[str] = None
    bootstrap_servers: Optional[str] = None
    topic: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    provider: Optional[str] = None  # For cloud storage: 's3', 'gcs', 'azure'
    options: Optional[Dict[str, Any]] = {}
    properties: Optional[Dict[str, Any]] = None


class BigDataAnalysisInput(BaseModel):
    """Big Data Analysis Input"""
    title: str = "Big Data Analysis Report"
    value_columns: Optional[List[str]] = None  # Multiple columns (NEW)
    source_config: SourceConfig
    numeric_columns: Optional[List[str]] = None
    time_column: Optional[str] = None
    value_column: Optional[str] = None
    group_columns: Optional[List[str]] = None
    perform_anomaly_detection: bool = False
    anomaly_method: str = Field(default="iqr", pattern="^(iqr|zscore)$")
    filters: Optional[List[Dict[str, Any]]] = None  # And this
    generate_visualizations: Optional[bool] = True  # And this
    analyses: Optional[List[str]] = None
    period: Optional[int] = Field(default=None, ge=1, le=365)
    model: str = Field(default="additive",
                       pattern="^(additive|multiplicative)$")

    @field_validator('period')
    @classmethod
    def validate_period(cls, v):
        if v is not None and v < 1:
            raise ValueError('period must be at least 1')
        return v

    @field_validator('numeric_columns', 'group_columns')
    @classmethod
    def validate_columns(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError('columns list cannot be empty')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "source_config": {
                    "type": "file",
                    "path": "/path/to/data.parquet",
                    "format": "parquet"
                },
                "numeric_columns": ["sales", "revenue", "quantity"],
                "time_column": "date",
                "value_column": "sales",
                "perform_anomaly_detection": True,
                "anomaly_method": "iqr",
                "period": 12,
                "model": "additive"
            }
        }
