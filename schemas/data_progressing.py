from pydantic import BaseModel
from schemas.descriptive_visualization import DescriptiveVisualizations
from typing import List, Optional, Union


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


# Define a type alias for all possible analysis input types
AnalysisInputType = Union[
    RegressionInput,
    DescriptiveAnalysisInput,
    Anova,
    CorrelationAnalysisInput,
    PCAInput,
    ClusterAnalysisInput,
    CCAInput
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
