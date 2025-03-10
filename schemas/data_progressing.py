from pydantic import BaseModel

class RegressionInput(BaseModel):
    """Regression Input"""
    regression_type: str = "linear"
    features_col: list
    label_col: str
    file_id: str
