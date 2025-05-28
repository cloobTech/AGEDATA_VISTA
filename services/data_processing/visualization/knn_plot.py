from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (

    confusion_matrix
)
import plotly.graph_objects as go
import numpy as np


def generate_knn_confusion_matrix(y_true, y_pred, class_names=None) -> dict:
    """Multiclass-compatible confusion matrix"""
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


def generate_knn_decision_boundary(model, X_test, y_test, feature_names) -> dict:
    """Generate 2D decision boundary visualization"""
    if len(feature_names) != 2:
        return {}  # Only works for 2 features

    # Create mesh grid
    x_min, x_max = X_test.iloc[:, 0].min() - 1, X_test.iloc[:, 0].max() + 1
    y_min, y_max = X_test.iloc[:, 1].min() - 1, X_test.iloc[:, 1].max() + 1
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
        x=X_test.iloc[:, 0],
        y=X_test.iloc[:, 1],
        mode='markers',
        marker=dict(
            color=y_test,
            colorscale=['red', 'blue'],
            size=8,
            line=dict(width=1, color='Black')
        ),
        name="Data Points"
    ))

    fig.update_layout(
        title="KNN Decision Boundary (k={})".format(model.n_neighbors),
        xaxis_title=feature_names[0],
        yaxis_title=feature_names[1]
    )

    return {"decision_boundary": fig.to_json()}


def generate_knn_metrics_plot(metrics: dict) -> dict:
    """Generate metrics bar chart"""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=list(metrics.keys()),
        y=list(metrics.values()),
        marker_color=['blue', 'green', 'orange']
    ))

    fig.update_layout(
        title="KNN Performance Metrics",
        yaxis_title="Score",
        yaxis_range=[0, 1]
    )

    return {"metrics_plot": fig.to_json()}


def generate_knn_elbow_curve(X_train, y_train, max_k: int = 20) -> dict:
    """Generate elbow curve for optimal k selection"""
    error_rates = []

    for k in range(1, max_k + 1):
        knn = KNeighborsClassifier(n_neighbors=k)
        knn.fit(X_train, y_train)
        pred_i = knn.predict(X_train)
        error_rates.append(np.mean(pred_i != y_train))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, max_k + 1)),
        y=error_rates,
        mode='lines+markers',
        name="Error Rate"
    ))

    fig.update_layout(
        title="Elbow Method for Optimal k",
        xaxis_title="Number of Neighbors (k)",
        yaxis_title="Error Rate"
    )

    return {"elbow_curve": fig.to_json()}
