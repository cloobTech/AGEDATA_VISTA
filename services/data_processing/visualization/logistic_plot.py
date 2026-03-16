import plotly.graph_objects as go
from sklearn.metrics import roc_curve, roc_auc_score, confusion_matrix, precision_recall_curve, auc
import numpy as np
import plotly.express as px


def generate_logistic_regression_plot(y_true, y_pred, y_proba, n_classes, class_names=None):
    """Generate professional plots for both binary and multi-class logistic regression"""
    visuals = {}

    # Use provided class names or generate defaults
    if class_names is None:
        class_names = [f"Class {i}" for i in range(n_classes)]

    # Confusion Matrix with professional styling
    cm = confusion_matrix(y_true, y_pred)
    
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
        textfont={"size": 11, "color": "black"},
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
            text="Logistic Regression - Confusion Matrix",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="Predicted Label",
        yaxis_title="True Label",
        xaxis=dict(
            tickangle=45,
            tickfont=dict(size=11),
            showgrid=False
        ),
        yaxis=dict(
            tickfont=dict(size=11),
            showgrid=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=700,
        height=600,
        margin=dict(l=80, r=50, t=100, b=100)
    )
    
    # Add colorbar with title
    fig.update_coloraxes(colorbar=dict(
        title=dict(text="Count", side="right"),
        tickvals=np.linspace(cm.min(), cm.max(), 5)
    ))
    
    visuals["confusion_matrix"] = fig.to_json()

    # ROC Curve (only for binary classification)
    if n_classes == 2 and y_proba is not None:
        fpr, tpr, thresholds = roc_curve(y_true, y_proba)
        auc_score = roc_auc_score(y_true, y_proba)

        fig = go.Figure()
        
        # ROC Curve with filled area
        fig.add_trace(go.Scatter(
            x=fpr, 
            y=tpr,
            mode='lines',
            name=f'ROC Curve (AUC = {auc_score:.3f})',
            line=dict(color='#1f77b4', width=3),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.2)',
            hovertemplate="FPR: %{x:.3f}<br>TPR: %{y:.3f}<br>Threshold: %{customdata:.3f}<extra></extra>",
            customdata=thresholds
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
        
        # Precision-Recall Curve (for binary classification)
        precision, recall, _ = precision_recall_curve(y_true, y_proba)
        pr_auc = auc(recall, precision)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=recall, 
            y=precision,
            mode='lines',
            name=f'Precision-Recall Curve (AUC = {pr_auc:.3f})',
            line=dict(color='#2ca02c', width=3),
            fill='tozeroy',
            fillcolor='rgba(44, 160, 44, 0.2)',
            hovertemplate="Recall: %{x:.3f}<br>Precision: %{y:.3f}<extra></extra>"
        ))
        
        # Add no-skill line
        no_skill = len(y_true[y_true == 1]) / len(y_true)
        fig.add_trace(go.Scatter(
            x=[0, 1], 
            y=[no_skill, no_skill],
            mode='lines',
            name='No Skill',
            line=dict(color='red', dash='dash', width=2),
            hovertemplate="No Skill Line<extra></extra>"
        ))
        
        fig.update_layout(
            title=dict(
                text=f"Precision-Recall Curve (AUC = {pr_auc:.3f})",
                x=0.05,
                xanchor='left',
                font=dict(size=20, color='#2a3f5f')
            ),
            xaxis_title="Recall",
            yaxis_title="Precision",
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
        
        visuals["precision_recall_curve"] = fig.to_json()
        
        # Probability Distribution Plot
        fig = go.Figure()
        
        # Histogram of predicted probabilities for each class
        for class_label in [0, 1]:
            mask = y_true == class_label
            fig.add_trace(go.Histogram(
                x=y_proba[mask],
                name=f"Class {class_label}",
                opacity=0.7,
                nbinsx=30,
                histnorm='probability density',
                marker_color='#1f77b4' if class_label == 0 else '#ff7f0e',
                hovertemplate="Probability: %{x:.3f}<br>Density: %{y:.3f}<extra></extra>"
            ))
        
        # Add decision threshold line (default 0.5)
        fig.add_vline(
            x=0.5, 
            line_dash="dash", 
            line_color="red",
            line_width=2,
            annotation_text="Decision Threshold (0.5)", 
            annotation_position="top right"
        )
        
        fig.update_layout(
            title=dict(
                text="Predicted Probability Distribution",
                x=0.05,
                xanchor='left',
                font=dict(size=20, color='#2a3f5f')
            ),
            xaxis_title="Predicted Probability",
            yaxis_title="Density",
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E5ECF6',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='#2a3f5f',
                range=[0, 1]
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
            width=800,
            height=500,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.9)'
            ),
            barmode='overlay'
        )
        
        visuals["probability_distribution"] = fig.to_json()

    # For multiclass classification, add additional visualizations
    elif n_classes > 2 and y_proba is not None:
        # Multiclass ROC Curve (one-vs-rest)
        from sklearn.preprocessing import label_binarize
        from sklearn.metrics import roc_curve, auc
        
        # Binarize the output
        y_true_bin = label_binarize(y_true, classes=range(n_classes))
        
        fig = go.Figure()
        
        # Compute ROC curve and ROC area for each class
        for i in range(n_classes):
            fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_proba[:, i])
            roc_auc = auc(fpr, tpr)
            
            fig.add_trace(go.Scatter(
                x=fpr, 
                y=tpr,
                mode='lines',
                name=f'{class_names[i]} (AUC = {roc_auc:.3f})',
                line=dict(width=2.5),
                hovertemplate=f"Class {class_names[i]}<br>FPR: %{{x:.3f}}<br>TPR: %{{y:.3f}}<extra></extra>"
            ))
        
        # Random classifier line
        fig.add_trace(go.Scatter(
            x=[0, 1], 
            y=[0, 1],
            mode='lines',
            name='Random Classifier',
            line=dict(color='black', dash='dash', width=2),
            hovertemplate="Random Classifier<extra></extra>"
        ))
        
        fig.update_layout(
            title=dict(
                text="Multiclass ROC Curves (One-vs-Rest)",
                x=0.05,
                xanchor='left',
                font=dict(size=20, color='#2a3f5f')
            ),
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            plot_bgcolor='white',
            paper_bgcolor='white',
            width=800,
            height=600,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.9)'
            )
        )
        
        visuals["multiclass_roc"] = fig.to_json()

    return visuals


# Additional: Coefficient plot for logistic regression
def generate_coefficient_plot(coefficients, feature_names, model_type="logistic"):
    """Generate coefficient plot for logistic regression"""
    fig = go.Figure()
    
    # Sort by absolute value for better visualization
    indices = np.argsort(np.abs(coefficients))[::-1]
    sorted_coef = coefficients[indices]
    sorted_names = [feature_names[i] for i in indices]
    
    colors = ['#2ca02c' if coef > 0 else '#d62728' for coef in sorted_coef]
    
    fig.add_trace(go.Bar(
        x=sorted_coef,
        y=sorted_names,
        orientation='h',
        marker_color=colors,
        marker_line_width=0,
        hovertemplate="Feature: %{y}<br>Coefficient: %{x:.4f}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text=f"{model_type.title()} Regression Coefficients",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="Coefficient Value",
        yaxis_title="Features",
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=800,
        height=600,
        margin=dict(l=150, r=50, t=100, b=80),
        showlegend=False
    )
    
    # Add zero reference line
    fig.add_vline(
        x=0, 
        line_width=2, 
        line_color='#2a3f5f',
        line_dash="solid"
    )
    
    return fig.to_json()