from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from services.data_processing.report import crud
from services.data_processing.visualization.regression_analysis import (
    linear_regression_plot,
    decision_tree_plot,
)
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_progressing import RegressionInput, AnalysisInput


async def perform_regression(data: pd.DataFrame, input: AnalysisInput, session: AsyncSession):
    """
    Perform regression using scikit-learn.

    :param regression_type: Type of regression ('linear', 'decision_tree', 'logistic')
    :param data: Input DataFrame
    :param features_col: List of feature columns
    :param label_col: Target column
    :return: Trained regression model and performance metrics
    """

    inputs: RegressionInput = input.analysis_input
    X = data[inputs.features_col].values
    y = data[inputs.label_col].values

    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    # Initialize and train the regression model
    if inputs.regression_type == 'linear':
        result = perform_linear_regression(
            X_train, X_test, y_train, y_test, input)
    elif inputs.regression_type == 'decision_tree':
        result = perform_decision_tree_regression(
            X_train, X_test, y_train, y_test, input)
    elif inputs.regression_type == 'logistic':
        result = perform_logistic_regression(
            X_train, X_test, y_train, y_test, input)
    else:
        raise ValueError(
            f"Unsupported regression type: {inputs.regression_type}. Use 'linear', 'decision_tree', or 'logistic'.")

    report_obj = {}
    report_obj["visualizations"] = result.pop("visualizations", {})
    report_obj['project_id'] = input.project_id
    report_obj['summary'] = result
    report_obj['title'] = input.title

    # Create Visualization

    # Create a report
    # report = await crud.create_report(report_obj, session=session)
    # return report
    return report_obj


def perform_linear_regression(X_train, X_test, y_train, y_test, input):
    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    response_content = {
        "RMSE": float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "R2": float(r2_score(y_test, y_pred)),
        "Coefficients": model.coef_.tolist(),
        "Intercept": float(model.intercept_)
    }

    if input.generate_visualizations:
        feature_names = input.analysis_input.features_col

        response_content["visualizations"] = linear_regression_plot(
            X_test, y_test, y_pred, feature_names)
    else:
        response_content["visualizations"] = {}
    return response_content


def perform_decision_tree_regression(X_train, X_test, y_train, y_test, input):
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
    if input.generate_visualizations:
        feature_names = input.analysis_input.features_col
        response_content["visualizations"] = decision_tree_plot(
            X_test, y_test, y_pred, feature_names)
    else:
        response_content["visualizations"] = {}
    return response_content


def perform_logistic_regression(X_train, X_test, y_train, y_test, input):
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
