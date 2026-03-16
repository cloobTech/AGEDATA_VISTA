from sklearn.metrics import (
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    mean_squared_error,
    mean_absolute_error,
    r2_score
)
import plotly.graph_objects as go
import numpy as np
import plotly.express as px


def generate_gb_classification_plots(y_true, y_pred, y_proba=None, class_names=None) -> dict:
    """Generate professional classification visualizations with proper class labels"""
    visuals = {}

    # Confusion Matrix with professional styling
    cm = confusion_matrix(y_true, y_pred)

    # Use provided class names or generate defaults
    if class_names is None:
        class_names = [f"Class {i}" for i in range(len(np.unique(y_true)))]

    # Calculate percentages for better interpretation
    cm_percent = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=class_names,
        y=class_names,
        colorscale='Blues',
        text=np.array([[f"{count}\n({percent:.1f}%)" for count, percent in zip(row, percent_row)]
                      for row, percent_row in zip(cm, cm_percent)]),
        texttemplate="%{text}",
        textfont={"size": 12, "color": "black"},
        hovertemplate=(
            "<b>True:</b> %{y}<br>" +
            "<b>Predicted:</b> %{x}<br>" +
            "<b>Count:</b> %{z}<br>" +
            "<b>Percentage:</b> %{text}<br>" +
            "<extra></extra>"
        )
    ))

    fig.update_layout(
        title=dict(
            text="Confusion Matrix",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="Predicted Label",
        yaxis_title="True Label",
        xaxis=dict(
            tickangle=45,
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            tickfont=dict(size=11)
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=700,
        height=600,
        margin=dict(l=80, r=50, t=100, b=100)
    )

    # Add colorbar with title
    fig.update_coloraxes(colorbar=dict(
        title=dict(text="Count", side="right")
    ))

    visuals["confusion_matrix"] = fig.to_json()

    # ROC Curve (for binary classification)
    if y_proba is not None and len(class_names) == 2:
        fpr, tpr, thresholds = roc_curve(y_true, y_proba)
        auc_score = roc_auc_score(y_true, y_proba)

        fig = go.Figure()

        # ROC Curve
        fig.add_trace(go.Scatter(
            x=fpr,
            y=tpr,
            mode='lines',
            name=f'ROC Curve (AUC = {auc_score:.3f})',
            line=dict(color='#1f77b4', width=3),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.2)',
            hovertemplate="FPR: %{x:.3f}<br>TPR: %{y:.3f}<extra></extra>"
        ))

        # Random classifier line
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode='lines',
            name='Random Classifier',
            line=dict(color='red', dash='dash', width=2),
            hovertemplate="Random Classifier<extra></extra>"
        ))

        fig.update_layout(
            title=dict(
                text=f"ROC Curve (AUC = {auc_score:.3f})",
                x=0.05,
                xanchor='left',
                font=dict(size=20, color='#2a3f5f')
            ),
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E5ECF6',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='#2a3f5f'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E5ECF6',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='#2a3f5f'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            width=700,
            height=600,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.9)'
            ),
            hovermode='closest'
        )

        visuals["roc_curve"] = fig.to_json()

    # Additional: Precision-Recall Curve could be added here

    return visuals


def generate_gb_regression_plots(y_true, y_pred) -> dict:
    """Generate professional regression visualizations"""
    residuals = y_true - y_pred

    # Calculate performance metrics
    mse = mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    metrics_text = f"<br><sup>MSE: {mse:.3f} | MAE: {mae:.3f} | R²: {r2:.3f}</sup>"

    # Actual vs Predicted with professional styling
    fig1 = go.Figure()

    # Predictions
    fig1.add_trace(go.Scatter(
        x=y_true,
        y=y_pred,
        mode='markers',
        name='Predictions',
        marker=dict(
            color='#1f77b4',
            size=8,
            opacity=0.7,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        hovertemplate="Actual: %{x:.3f}<br>Predicted: %{y:.3f}<extra></extra>"
    ))

    # Perfect prediction line
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())

    fig1.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        name='Perfect Prediction',
        line=dict(color='red', dash='dash', width=2.5),
        hovertemplate="Perfect Prediction Line<extra></extra>"
    ))

    fig1.update_layout(
        title=dict(
            text=f"Actual vs Predicted{metrics_text}",
            x=0.05,
            xanchor='left',
            font=dict(size=18, color='#2a3f5f')
        ),
        xaxis_title="Actual Values",
        yaxis_title="Predicted Values",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=700,
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        hovermode='closest'
    )

    # Residual Plot with professional styling
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=y_pred,
        y=residuals,
        mode='markers',
        name='Residuals',
        marker=dict(
            color='#ff7f0e',
            size=8,
            opacity=0.7,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        hovertemplate="Predicted: %{x:.3f}<br>Residual: %{y:.3f}<extra></extra>"
    ))

    # Zero reference line
    fig2.add_hline(
        y=0,
        line_dash='dash',
        line_color='red',
        line_width=2,
        annotation_text="Zero Residual",
        annotation_position="top right"
    )

    # Add confidence bands (2 standard deviations)
    residual_std = np.std(residuals)
    if np.isfinite(residual_std) and residual_std > 0:
        fig2.add_hrect(
            y0=-2*residual_std,
            y1=2*residual_std,
            fillcolor="rgba(0, 0, 0, 0.1)",
            line_width=0,
            annotation_text="±2σ",
            annotation_position="bottom right"
        )

    fig2.update_layout(
        title=dict(
            text="Residual Analysis",
            x=0.05,
            xanchor='left',
            font=dict(size=18, color='#2a3f5f')
        ),
        xaxis_title="Predicted Values",
        yaxis_title="Residuals",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=700,
        height=600,
        showlegend=False,
        hovermode='closest'
    )

    return {
        "actual_vs_predicted": fig1.to_json(),
        "residual_plot": fig2.to_json()
    }


def generate_feature_importance(model, feature_names) -> dict:
    """Generate professional feature importance plot"""
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    # Get top 20 features if there are many
    if len(importances) > 20:
        indices = indices[:20]
        importances = importances[indices]
        feature_names = [feature_names[i] for i in indices]

    fig = go.Figure(go.Bar(
        x=importances,
        y=feature_names,
        orientation='h',
        marker_color='#1f77b4',
        marker_line_width=0,
        hovertemplate="Feature: %{y}<br>Importance: %{x:.4f}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text="Feature Importance",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="Importance Score",
        yaxis_title="Features",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=800,
        height=600,
        margin=dict(l=150, r=50, t=100, b=80)
    )

    return {"feature_importance": fig.to_json()}


# Additional: Classification report visualization
def generate_classification_report_visualization(y_true, y_pred, class_names=None):
    """Generate a visual classification report"""
    from sklearn.metrics import classification_report
    import pandas as pd

    report = classification_report(
        y_true, y_pred, output_dict=True, target_names=class_names)
    report_df = pd.DataFrame(report).transpose().round(3)

    # Create heatmap for the report
    fig = go.Figure(data=go.Heatmap(
        z=report_df[['precision', 'recall', 'f1-score']].values,
        x=['Precision', 'Recall', 'F1-Score'],
        y=report_df.index,
        colorscale='Viridis',
        text=report_df[['precision', 'recall', 'f1-score']].values,
        texttemplate="%{text:.3f}",
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.3f}<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text="Classification Report",
            x=0.05,
            xanchor='left'
        ),
        width=600,
        height=400
    )

    return fig.to_json()
