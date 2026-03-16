from sklearn.metrics import (
    confusion_matrix,
)
import plotly.graph_objects as go
import numpy as np


def generate_svm_confusion_matrix(y_true, y_pred, class_names=None) -> dict:
    """Multiclass-compatible confusion matrix"""

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)

    if class_names is None:
        class_names = [f"Class {i}" for i in range(cm.shape[0])]

    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=class_names,
        y=class_names,
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


def generate_svm_decision_boundary(model, X_test, y_test) -> dict:
    """Generate 2D decision boundary visualization"""
    if X_test.shape[1] != 2:
        return {}  # Only works for 2 features

    # Normalise to numpy so both DataFrame and ndarray inputs work
    X_arr = X_test.values if hasattr(X_test, 'values') else np.asarray(X_test)

    # Create mesh grid
    x_min, x_max = X_arr[:, 0].min() - 1, X_arr[:, 0].max() + 1
    y_min, y_max = X_arr[:, 1].min() - 1, X_arr[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.02),
                         np.arange(y_min, y_max, 0.02))

    # Predict for mesh grid
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Create plot
    fig = go.Figure()

    # Decision boundary
    fig.add_trace(go.Contour(
        x=np.arange(x_min, x_max, 0.02),
        y=np.arange(y_min, y_max, 0.02),
        z=Z,
        colorscale='RdBu',
        opacity=0.5,
        showscale=False,
        name="Decision Boundary"
    ))

    # Actual data points
    fig.add_trace(go.Scatter(
        x=X_arr[:, 0],
        y=X_arr[:, 1],
        mode='markers',
        marker=dict(
            color=y_test,
            colorscale=['red', 'blue'],
            size=8,
            line=dict(width=1, color='Black')
        ),
        name="Data Points"
    ))

    col_names = list(X_test.columns) if hasattr(X_test, 'columns') else ["Feature 1", "Feature 2"]
    fig.update_layout(
        title="SVM Decision Boundary",
        xaxis_title=col_names[0],
        yaxis_title=col_names[1]
    )

    return {"decision_boundary": fig.to_json()}


def generate_svm_metrics_plot(metrics: dict) -> dict:
    """Generate metrics bar chart"""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=list(metrics.keys()),
        y=list(metrics.values()),
        marker_color=['blue', 'green', 'orange']
    ))

    fig.update_layout(
        title="Model Performance Metrics",
        yaxis_title="Score",
        yaxis_range=[0, 1]
    )

    return {"metrics_plot": fig.to_json()}
