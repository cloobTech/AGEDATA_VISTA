from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
from schemas.data_processing import KNNConfig
from services.data_processing.helper.preprocessor import prepare_X


def train_knn(
    X: pd.DataFrame,
    y: pd.Series,
    config: KNNConfig,
    test_size: float,
    task_type: str
) -> dict:
    """Train and evaluate KNN model"""
    # Encode categorical feature columns and fill missing values before scaling
    X, _enc_map = prepare_X(X)

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

    # Scale features (required for distance-based KNN)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Train model
    model.fit(X_train, y_train)

    # Generate predictions
    y_pred = model.predict(X_test)
    if task_type == "classification":
        _proba = model.predict_proba(X_test)
        y_proba = _proba[:, 1] if _proba.shape[1] == 2 else _proba
    else:
        y_proba = None

    return {
        "model": model,
        "scaler": scaler,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred,
        "y_proba": y_proba,
        "X_train": X_train,
        "y_train": y_train
    }
