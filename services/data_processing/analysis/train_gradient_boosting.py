from xgboost import XGBClassifier, XGBRegressor
from lightgbm import LGBMClassifier, LGBMRegressor
from sklearn.model_selection import train_test_split
from schemas.data_progressing import (
    GradientBoostingType,
    GradientBoostingConfig,
)

import plotly.graph_objects as go
import pandas as pd

def train_gradient_boosting(
    X: pd.DataFrame,
    y: pd.Series,
    model_type: GradientBoostingType,
    config: GradientBoostingConfig,
    test_size: float,
    task_type: str
) -> dict:
    """Train and evaluate gradient boosting model"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=config.random_state
    )
    
    if model_type == GradientBoostingType.XGBOOST:
        if task_type == "classification":
            model = XGBClassifier(
                n_estimators=config.n_estimators,
                learning_rate=config.learning_rate,
                max_depth=config.max_depth,
                gamma=config.gamma,
                reg_alpha=config.reg_alpha,
                reg_lambda=config.reg_lambda,
                subsample=config.subsample,
                random_state=config.random_state,
                use_label_encoder=False,
                eval_metric='logloss'
            )
        else:
            model = XGBRegressor(
                n_estimators=config.n_estimators,
                learning_rate=config.learning_rate,
                max_depth=config.max_depth,
                gamma=config.gamma,
                reg_alpha=config.reg_alpha,
                reg_lambda=config.reg_lambda,
                subsample=config.subsample,
                random_state=config.random_state
            )
    else:  # LightGBM
        if task_type == "classification":
            model = LGBMClassifier(
                n_estimators=config.n_estimators,
                learning_rate=config.learning_rate,
                num_leaves=config.num_leaves,
                max_depth=config.max_depth,
                min_child_samples=config.min_child_samples,
                subsample=config.subsample,
                random_state=config.random_state
            )
        else:
            model = LGBMRegressor(
                n_estimators=config.n_estimators,
                learning_rate=config.learning_rate,
                num_leaves=config.num_leaves,
                max_depth=config.max_depth,
                min_child_samples=config.min_child_samples,
                subsample=config.subsample,
                random_state=config.random_state
            )
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    return {
        "model": model,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred,
        "y_proba": model.predict_proba(X_test)[:, 1] if task_type == "classification" else None
    }