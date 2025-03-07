from pyspark.ml.regression import LinearRegression, DecisionTreeRegressor
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import VectorAssembler


def perform_regression(regression_type: str, data, features_col: list, label_col: str):
    """
    Perform linear regression on the given data.

    :param spark: Spark session
    :param data: Input DataFrame
    :param features_col: List of feature columns
    :param label_col: Target column
    :return: Trained regression model
    """
    # Assemble features into a vector
    assembler = VectorAssembler(inputCols=features_col, outputCol="features")
    data = assembler.transform(data)

    # Split data into training and test sets
    train_data, test_data = data.randomSplit([0.8, 0.2], seed=42)

    # Initialize and train the regression model
    if regression_type == 'linear':
        response_content = perform_linear_regression(label_col, train_data)
    elif regression_type == 'decision_tree':
        response_content = perform_decision_tree_regression(
            label_col, train_data)
    elif regression_type == 'logistic':
        lr = LogisticRegression(featuresCol="features", labelCol=label_col)
        model = lr.fit(train_data)
    else:
        raise ValueError(
            f"Unsupported regression type: {regression_type}. Use 'linear'.")

    return response_content


def perform_linear_regression(label_col, train_data):
    lr = LinearRegression(featuresCol="features", labelCol=label_col)
    model = lr.fit(train_data)
    response_content = {
        "RMSE": model.summary.rootMeanSquaredError,
        "R2": model.summary.r2,
        "Coefficients": model.coefficients.tolist(),
        "Intercept": model.intercept,
    }
    return response_content


def perform_decision_tree_regression(label_col, train_data):
    dt = DecisionTreeRegressor(featuresCol="features", labelCol=label_col)
    model = dt.fit(train_data)
    response_content = {
        "Feature Importances": model.featureImportances.toArray().tolist(),
        "Depth": model.depth,
        "Num Nodes": model.numNodes
    }
    return response_content
