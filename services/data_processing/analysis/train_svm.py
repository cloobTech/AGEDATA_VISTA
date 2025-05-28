from sklearn.svm import SVC, SVR
from sklearn.model_selection import train_test_split
import pandas as pd
from schemas.data_processing import SVMConfig


def train_svm(
    X: pd.DataFrame,
    y: pd.Series,
    config: SVMConfig,
    test_size: float,
    task_type: str
) -> dict:
    """Train and evaluate SVM model"""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=config.random_state
    )

    # Initialize appropriate SVM model
    if task_type == "classification":
        model = SVC(
            C=config.C,
            kernel=config.kernel.value,
            degree=config.degree,
            gamma=config.gamma,
            probability=config.probability,
            random_state=config.random_state
        )
    else:
        model = SVR(
            C=config.C,
            kernel=config.kernel.value,
            degree=config.degree,
            gamma=config.gamma
        )

    # Train model
    model.fit(X_train, y_train)

    # Generate predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(
        model, "predict_proba") else None

    return {
        "model": model,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred,
        "y_proba": y_proba
    }
