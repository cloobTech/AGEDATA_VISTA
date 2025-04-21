
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio


def linear_regression_plot(X_test, y_test, y_pred, feature_names=None) -> dict:
    num_features = X_test.shape[1]

    if feature_names is None:
        feature_names = [f"Feature {i+1}" for i in range(num_features)]

    # Convert to DataFrame for easier px usage
    df = pd.DataFrame(X_test, columns=feature_names)
    df['Actual'] = y_test
    df['Predicted'] = y_pred

    plots = {}

    if num_features == 1:
        feature = feature_names[0]
        fig = px.scatter(df, x=feature, y='Actual', title='Linear Regression (1D)')
        fig.add_traces(px.line(df.sort_values(by=feature), x=feature, y='Predicted').data)
        plots["linear_reg_plot"] = pio.to_json(fig)
    else:
        for feature in feature_names:
            fig = px.scatter(df, x=feature, y='Actual', title=f'{feature} vs Target')
            fig.add_traces(px.line(df.sort_values(by=feature), x=feature, y='Predicted').data)
            plots[feature] = pio.to_json(fig)

    return plots


def decision_tree_plot(X_test, y_test, y_pred, feature_names=None) -> dict:
    plots = {}

    if feature_names is None:
        feature_names = [f"Feature {i+1}" for i in range(X_test.shape[1])]

    for idx, feature in enumerate(feature_names):
        df = pd.DataFrame({
            feature: X_test[:, idx],
            "Actual": y_test,
            "Predicted": y_pred
        })

        fig = px.scatter(df, x=feature, y='Actual', title=f'Decision Tree: {feature}')
        fig.add_traces(px.scatter(df, x=feature, y='Predicted', color_discrete_sequence=["red"]).data)
        plots[feature] = pio.to_json(fig)

    return plots
