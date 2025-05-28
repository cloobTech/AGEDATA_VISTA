from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
from schemas.data_processing import KNNConfig


def train_knn(
    X: pd.DataFrame,
    y: pd.Series,
    config: KNNConfig,
    test_size: float,
    task_type: str
) -> dict:
    """Train and evaluate KNN model"""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )

    # Initialize appropriate KNN model
    if task_type == "classification":
        model = KNeighborsClassifier(
            n_neighbors=config.n_neighbors,
            weights=config.weights.value,
            algorithm=config.algorithm.value,
            p=config.p,
            metric=config.metric
        )
    else:
        model = KNeighborsRegressor(
            n_neighbors=config.n_neighbors,
            weights=config.weights.value,
            algorithm=config.algorithm.value,
            p=config.p,
            metric=config.metric
        )

    # Train model
    model.fit(X_train, y_train)

    # Generate predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(
        X_test)[:, 1] if task_type == "classification" else None

    return {
        "model": model,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred,
        "y_proba": y_proba,
        "X_train": X_train,
        "y_train": y_train
    }
