from pydantic import BaseModel
from schemas.descriptive_visualization import DescriptiveVisualizations


class RegressionInput(BaseModel):
    """Regression Input"""
    regression_type: str = "linear"
    features_col: list
    label_col: str
    file_id: str
    project_id: str


class DescriptiveAnalysisInput(BaseModel):
    """Descriptive Analysis Input"""
    file_id: str
    project_id: str
    generate_visualizations: bool = False
    visualization_list: list = []
    descriptive_visualizations: DescriptiveVisualizations = None
