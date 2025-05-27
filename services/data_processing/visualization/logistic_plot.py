import plotly.graph_objects as go
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix


def generate_logistic_regression_plot(y_true, y_pred, y_proba, n_classes):
    """Generate plots for both binary and multi-class logistic regression"""
    visuals = {}

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=[f"Predicted {i}" for i in range(n_classes)],
        y=[f"Actual {i}" for i in range(n_classes)],
        colorscale='Blues',
        text=cm,
        texttemplate="%{text}"
    ))
    fig.update_layout(title="Confusion Matrix")
    visuals["confusion_matrix"] = fig.to_json()

    # ROC Curve (only for binary classification)
    if n_classes == 2 and y_proba is not None:
        fpr, tpr, _ = roc_curve(y_true, y_proba)
        auc_score = roc_auc_score(y_true, y_proba)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=fpr, y=tpr,
            mode='lines',
            name=f'ROC Curve (AUC = {auc_score:.2f})',
            line=dict(color='blue')))
        fig.add_trace(go.Scatter(
            x=[0, 1], y=[0, 1],
            mode='lines',
            line=dict(color='red', dash='dash'),
            showlegend=False))
        fig.update_layout(
            title="ROC Curve",
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate"
        )
        visuals["roc_curve"] = fig.to_json()

    return visuals
