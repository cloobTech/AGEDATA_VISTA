from pydantic import BaseModel
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


class AnalysisInput(BaseModel):
    """Base Analysis Input"""
    analysis_group: str
    columns: list = []
    analysis_type: str
    generate_visualizations: bool = False
    analysis_input: RegressionInput | DescriptiveAnalysisInput
    title: str = "Analysis Report"
    project_id: str
    file_id: str
