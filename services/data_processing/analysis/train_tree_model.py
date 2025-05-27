from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
from schemas.data_progressing import (
    TreeModelType, TreeModelConfig
)


def train_tree_model(
    X: pd.DataFrame,
    y: pd.Series,
    model_type: TreeModelType,
    config: TreeModelConfig,
    test_size: float,
    task_type: str
) -> dict:
    """Train and evaluate a tree-based model"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=config.random_state
    )

    if model_type == TreeModelType.DECISION_TREE:
        if task_type == "classification":
            model = DecisionTreeClassifier(
                max_depth=config.max_depth,
                min_samples_split=config.min_samples_split,
                min_samples_leaf=config.min_samples_leaf,
                criterion=config.criterion,
                random_state=config.random_state
            )
        else:
            model = DecisionTreeRegressor(
                max_depth=config.max_depth,
                min_samples_split=config.min_samples_split,
                min_samples_leaf=config.min_samples_leaf,
                criterion="squared_error",
                random_state=config.random_state
            )
    else:  # Random Forest
        if task_type == "classification":
            model = RandomForestClassifier(
                n_estimators=config.n_estimators,
                max_depth=config.max_depth,
                min_samples_split=config.min_samples_split,
                min_samples_leaf=config.min_samples_leaf,
                criterion=config.criterion,
                max_features=config.max_features,
                random_state=config.random_state
            )
        else:
            model = RandomForestRegressor(
                n_estimators=config.n_estimators,
                max_depth=config.max_depth,
                min_samples_split=config.min_samples_split,
                min_samples_leaf=config.min_samples_leaf,
                criterion="squared_error",
                max_features=config.max_features,
                random_state=config.random_state
            )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    return {
        "model": model,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred
    }
