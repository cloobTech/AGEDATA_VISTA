from pydantic import BaseModel
from schemas.descriptive_visualization import DescriptiveVisualizations


class RegressionInput(BaseModel):
    """Regression Input"""
    columns: list = []
    regression_type: str = "linear"
    features_col: list
    label_col: str
    file_id: str
    project_id: str
    title: str = "Regression Analysis"


class DescriptiveAnalysisInput(BaseModel):
    """Descriptive Analysis Input"""
    columns: list = []
    file_id: str
    project_id: str
    generate_visualizations: bool = False
    visualization_list: list = []
    descriptive_visualizations: DescriptiveVisualizations = None
    title: str = "Descriptive Analysis"
