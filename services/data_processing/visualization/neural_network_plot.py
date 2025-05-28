
from sklearn.metrics import (
    confusion_matrix, roc_auc_score, roc_curve,
)
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots


def generate_nn_training_plots(history) -> dict:
    """Generate training history visualizations"""
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Loss", "Accuracy"))

    # Loss plot
    fig.add_trace(go.Scatter(
        x=list(range(len(history['loss']))),
        y=history['loss'],
        name="Training Loss",
        line=dict(color='blue')
    ), row=1, col=1)

    if 'val_loss' in history:
        fig.add_trace(go.Scatter(
            x=list(range(len(history['val_loss']))),
            y=history['val_loss'],
            name="Validation Loss",
            line=dict(color='red')
        ), row=1, col=1)

    # Accuracy plot (if classification)
    if 'accuracy' in history:
        fig.add_trace(go.Scatter(
            x=list(range(len(history['accuracy']))),
            y=history['accuracy'],
            name="Training Accuracy",
            line=dict(color='blue'),
            showlegend=False
        ), row=1, col=2)

        if 'val_accuracy' in history:
            fig.add_trace(go.Scatter(
                x=list(range(len(history['val_accuracy']))),
                y=history['val_accuracy'],
                name="Validation Accuracy",
                line=dict(color='red'),
                showlegend=False
            ), row=1, col=2)

    fig.update_layout(
        title="Training History",
        hovermode="x unified"
    )
    fig.update_xaxes(title_text="Epochs", row=1, col=1)
    fig.update_xaxes(title_text="Epochs", row=1, col=2)
    fig.update_yaxes(title_text="Loss", row=1, col=1)

    if 'accuracy' in history:
        fig.update_yaxes(title_text="Accuracy", row=1, col=2)

    return {"training_history": fig.to_json()}


def generate_nn_confusion_matrix(y_true, y_pred, class_names=None) -> dict:
    """Generate confusion matrix with optional class names"""
    cm = confusion_matrix(y_true, y_pred)

    if class_names is None:
        class_names = [f"Class {i}" for i in range(len(np.unique(y_true)))]

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


def generate_nn_roc_curve(y_true, y_proba, class_names=None) -> dict:
    """Generate ROC curve for binary classification"""
    if len(np.unique(y_true)) != 2:
        return {}  # Only for binary classification

    fpr, tpr, _ = roc_curve(y_true, y_proba)
    auc_score = roc_auc_score(y_true, y_proba)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr,
        mode='lines',
        name=f'ROC Curve (AUC = {auc_score:.2f})',
        line=dict(color='blue'))
    )
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines',
        line=dict(color='red', dash='dash'),
        showlegend=False
    ))
    fig.update_layout(
        title="ROC Curve",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate"
    )
    return {"roc_curve": fig.to_json()}


def generate_nn_feature_importance(model, feature_names) -> dict:
    """Generate feature importance based on first layer weights"""
    weights = model.layers[0].get_weights()[0]
    importance = np.mean(np.abs(weights), axis=1)

    fig = go.Figure(go.Bar(
        x=importance,
        y=feature_names,
        orientation='h',
        marker_color='skyblue'
    ))
    fig.update_layout(
        title="Feature Importance (First Layer Weights)",
        xaxis_title="Importance Score",
        yaxis_title="Features"
    )
    return {"feature_importance": fig.to_json()}
