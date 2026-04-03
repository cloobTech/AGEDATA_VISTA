from sklearn.svm import SVC, SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
from schemas.data_processing import SVMConfig
from services.data_processing.helper.preprocessor import prepare_X


def train_svm(
    X: pd.DataFrame,
    y: pd.Series,
    config: SVMConfig,
    test_size: float,
    task_type: str
) -> dict:
    """Train and evaluate SVM model"""
    # Encode categorical feature columns and fill missing values before scaling
    X, _enc_map = prepare_X(X)

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

    # Scale features (required for kernel-based SVM)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Train model
    model.fit(X_train, y_train)

    # Generate predictions
    y_pred = model.predict(X_test)
    if hasattr(model, "predict_proba"):
        _proba = model.predict_proba(X_test)
        y_proba = _proba[:, 1] if _proba.shape[1] == 2 else _proba
    else:
        y_proba = None

    return {
        "model": model,
        "scaler": scaler,
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred,
        "y_proba": y_proba
    }
