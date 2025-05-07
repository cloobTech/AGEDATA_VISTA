from pydantic import BaseModel
from schemas.descriptive_visualization import DescriptiveVisualizations
from typing import List, Optional


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


class AnalysisInput(BaseModel):
    """Base Analysis Input"""
    analysis_group: str
    columns: list = []
    analysis_type: str
    generate_visualizations: bool = False
    analysis_input: RegressionInput | DescriptiveAnalysisInput | Anova
    title: str = "Analysis Report"
    project_id: str
    file_id: str
