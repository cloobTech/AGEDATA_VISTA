from sklearn.metrics import (

    confusion_matrix
)

import plotly.graph_objects as go
import numpy as np


def generate_tree_confusion_matrix(y_true, y_pred, classes=None) -> dict:
    """Generate interactive confusion matrix"""
    cm = confusion_matrix(y_true, y_pred)
    if classes is None:
        classes = sorted(set(y_true) | set(y_pred))

    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=[f"Predicted {cls}" for cls in classes],
        y=[f"Actual {cls}" for cls in classes],
        colorscale='Blues',
        text=cm,
        texttemplate="%{text}"
    ))
    fig.update_layout(
        title="Confusion Matrix",
        xaxis_title="Predicted Label",
        yaxis_title="True Label"
    )
    return {"confusion_matrix": fig.to_json()}


def generate_feature_importance(model, feature_names) -> dict:
    """Generate interactive feature importance plot"""
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    fig = go.Figure(go.Bar(
        x=importances[indices],
        y=[feature_names[i] for i in indices],
        orientation='h',
        marker_color='skyblue'
    ))
    fig.update_layout(
        title="Feature Importance",
        xaxis_title="Importance Score",
        yaxis_title="Features"
    )
    return {"feature_importance": fig.to_json()}


def generate_regression_plots(y_true, y_pred) -> dict:
    """Generate regression evaluation plots"""
    residuals = y_true - y_pred

    # Actual vs Predicted
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=y_true, y=y_pred,
        mode='markers',
        name='Predictions'
    ))
    fig1.add_trace(go.Scatter(
        x=[y_true.min(), y_true.max()],
        y=[y_true.min(), y_true.max()],
        mode='lines',
        name='Perfect Prediction',
        line=dict(color='red', dash='dash')
    ))
    fig1.update_layout(
        title="Actual vs Predicted",
        xaxis_title="Actual Values",
        yaxis_title="Predicted Values"
    )

    # Residual Plot
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=y_pred, y=residuals,
        mode='markers',
        name='Residuals'
    ))
    fig2.add_hline(y=0, line_dash='dash', line_color='red')
    fig2.update_layout(
        title="Residual Plot",
        xaxis_title="Predicted Values",
        yaxis_title="Residuals"
    )

    return {
        "actual_vs_predicted": fig1.to_json(),
        "residual_plot": fig2.to_json()
    }
