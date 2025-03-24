from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from services.data_processing.report.crud import create_report
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_progressing import RegressionInput


async def perform_regression(inputs: RegressionInput, data: pd.DataFrame, session: AsyncSession):
    """
    Perform regression using scikit-learn.

    :param regression_type: Type of regression ('linear', 'decision_tree', 'logistic')
    :param data: Input DataFrame
    :param features_col: List of feature columns
    :param label_col: Target column
    :return: Trained regression model and performance metrics
    """
    X = data[inputs.features_col].values
    y = data[inputs.label_col].values

    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    # Initialize and train the regression model
    if inputs.regression_type == 'linear':
        result = perform_linear_regression(X_train, X_test, y_train, y_test)
    elif inputs.regression_type == 'decision_tree':
        result = perform_decision_tree_regression(
            X_train, X_test, y_train, y_test)
    elif inputs.regression_type == 'logistic':
        result = perform_logistic_regression(X_train, X_test, y_train, y_test)
    else:
        raise ValueError(
            f"Unsupported regression type: {inputs.regression_type}. Use 'linear', 'decision_tree', or 'logistic'.")

    report_obj = {}
    report_obj['project_id'] = inputs.project_id
    report_obj['result'] = result
    report_obj['title'] = f"Titke Regression"

    # Create a report
    report = await create_report(report_obj, session=session)
    return report
    # await report.save(session=session)
    # return report.to_dict()


def perform_linear_regression(X_train, X_test, y_train, y_test):
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    response_content = {
        "RMSE": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "R2": float(r2_score(y_test, y_pred)),
        "Coefficients": model.coef_.tolist(),
        "Intercept": float(model.intercept_)
    }
    return response_content


def perform_decision_tree_regression(X_train, X_test, y_train, y_test):
    model = DecisionTreeRegressor(random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    response_content = {
        "RMSE": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "Feature Importances": model.feature_importances_.tolist(),
        "Depth": int(model.get_depth()),
        "Num Nodes": int(model.get_n_leaves()),
        "R2": float(r2_score(y_test, y_pred))
    }
    return response_content


def perform_logistic_regression(X_train, X_test, y_train, y_test):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)

    response_content = {
        "Coefficients": model.coef_.tolist(),
        "Intercept": model.intercept_.tolist(),
        "Score": float(model.score(X_test_scaled, y_test))
    }
    return response_content
