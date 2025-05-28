
from sklearn.metrics import (
    confusion_matrix,
    roc_auc_score, roc_curve
)
import plotly.graph_objects as go
import numpy as np


def generate_gb_classification_plots(y_true, y_pred, y_proba=None, class_names=None) -> dict:
    """Generate classification visualizations with proper class labels"""
    visuals = {}
    
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Use provided class names or generate defaults
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
    visuals["confusion_matrix"] = fig.to_json()
    
    # ROC Curve (for binary classification)
    if y_proba is not None and len(class_names) == 2:
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
        visuals["roc_curve"] = fig.to_json()
    
    return visuals

def generate_gb_regression_plots(y_true, y_pred) -> dict:
    """Generate regression visualizations"""
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

def generate_feature_importance(model, feature_names) -> dict:
    """Generate feature importance plot (works for both XGBoost and LightGBM)"""
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