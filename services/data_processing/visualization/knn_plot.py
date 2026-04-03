from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd


def generate_knn_confusion_matrix(y_true, y_pred, class_names=None) -> dict:
    """Multiclass-compatible confusion matrix with professional styling"""
    cm = confusion_matrix(y_true, y_pred)
    
    if class_names is None:
        class_names = [f"Class {i}" for i in range(cm.shape[0])]
    
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
            text="KNN Confusion Matrix",
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
    
    return {"confusion_matrix": fig.to_json()}


def generate_knn_decision_boundary(model, X_test, y_test, feature_names) -> dict:
    """Generate professional 2D decision boundary visualization"""
    if len(feature_names) != 2:
        return {}  # Only works for 2 features

    # Create mesh grid with appropriate resolution
    X_arr = X_test if isinstance(X_test, np.ndarray) else X_test.values
    x_min, x_max = X_arr[:, 0].min() - 0.5, X_arr[:, 0].max() + 0.5
    y_min, y_max = X_arr[:, 1].min() - 0.5, X_arr[:, 1].max() + 0.5
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200),
                         np.linspace(y_min, y_max, 200))

    # Predict for mesh grid
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    # Get unique classes and create color scale
    unique_classes = np.unique(y_test)
    colorscale = px.colors.qualitative.Plotly
    
    # Create plot
    fig = go.Figure()

    # Decision boundary as contour
    fig.add_trace(go.Contour(
        x=np.linspace(x_min, x_max, 200),
        y=np.linspace(y_min, y_max, 200),
        z=Z,
        colorscale=colorscale[:len(unique_classes)],
        opacity=0.4,
        showscale=False,
        name="Decision Regions",
        contours=dict(
            showlines=False
        ),
        hoverinfo='skip'
    ))

    # Actual data points with professional styling
    for i, class_label in enumerate(unique_classes):
        class_mask = y_test == class_label
        fig.add_trace(go.Scatter(
            x=X_arr[class_mask, 0],
            y=X_arr[class_mask, 1],
            mode='markers',
            marker=dict(
                size=10,
                color=colorscale[i % len(colorscale)],
                line=dict(width=1.5, color='white'),
                opacity=0.8
            ),
            name=f"Class {class_label}",
            hovertemplate=(
                f"{feature_names[0]}: %{{x:.2f}}<br>" +
                f"{feature_names[1]}: %{{y:.2f}}<br>" +
                f"Class: {class_label}<br>" +
                "<extra></extra>"
            )
        ))

    fig.update_layout(
        title=dict(
            text=f"KNN Decision Boundary (k={model.n_neighbors})",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title=feature_names[0],
        yaxis_title=feature_names[1],
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            showline=True,
            linewidth=2,
            linecolor='#2a3f5f'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            showline=True,
            linewidth=2,
            linecolor='#2a3f5f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=800,
        height=700,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#E5ECF6',
            borderwidth=1
        ),
        hovermode='closest'
    )

    return {"decision_boundary": fig.to_json()}


def generate_knn_metrics_plot(metrics: dict) -> dict:
    """Generate professional metrics bar chart"""
    fig = go.Figure()

    # Use Plotly's qualitative colors
    colors = px.colors.qualitative.Plotly

    # Only plot scalar numeric metrics
    _SKIP = {"classification_report", "confusion_matrix", "baseline", "roc_auc_note"}
    numeric_metrics = {k: v for k, v in metrics.items() if k not in _SKIP and isinstance(v, (int, float))}

    fig.add_trace(go.Bar(
        x=list(numeric_metrics.keys()),
        y=list(numeric_metrics.values()),
        marker_color=colors[:len(numeric_metrics)],
        marker_line_width=0,
        text=[f"{v:.3f}" for v in numeric_metrics.values()],
        textposition='auto',
        textfont=dict(size=12, color='white'),
        hovertemplate="<b>%{x}</b><br>Score: %{y:.3f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text="KNN Performance Metrics",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="Metric",
        yaxis_title="Score",
        yaxis=dict(
            range=[0, 1.05],
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f'
        ),
        xaxis=dict(
            showgrid=False,
            zeroline=False
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=600,
        height=500,
        margin=dict(l=80, r=50, t=100, b=80)
    )

    return {"metrics_plot": fig.to_json()}


def generate_knn_elbow_curve(X_train, y_train, max_k: int = 20) -> dict:
    """Generate professional elbow curve for optimal k selection"""
    error_rates = []
    accuracy_scores = []

    for k in range(1, max_k + 1):
        knn = KNeighborsClassifier(n_neighbors=k)
        knn.fit(X_train, y_train)
        pred_i = knn.predict(X_train)
        error_rates.append(np.mean(pred_i != y_train))
        accuracy_scores.append(accuracy_score(y_train, pred_i))

    # Find optimal k (elbow point)
    optimal_k = np.argmin(error_rates) + 1

    fig = go.Figure()

    # Error rate
    fig.add_trace(go.Scatter(
        x=list(range(1, max_k + 1)),
        y=error_rates,
        mode='lines+markers',
        name="Error Rate",
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=8),
        hovertemplate="k=%{x}<br>Error Rate: %{y:.3f}<extra></extra>"
    ))

    # Accuracy
    fig.add_trace(go.Scatter(
        x=list(range(1, max_k + 1)),
        y=accuracy_scores,
        mode='lines+markers',
        name="Accuracy",
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=8),
        hovertemplate="k=%{x}<br>Accuracy: %{y:.3f}<extra></extra>",
        yaxis="y2"
    ))

    # Highlight optimal k
    fig.add_vline(
        x=optimal_k,
        line_dash="dash",
        line_color="red",
        line_width=2,
        annotation_text=f"Optimal k={optimal_k}",
        annotation_position="top right"
    )

    fig.update_layout(
        title=dict(
            text="Elbow Method for Optimal k Selection",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="Number of Neighbors (k)",
        yaxis_title="Error Rate",
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f',
            range=[0, max(error_rates) * 1.1]
        ),
        yaxis2=dict(
            title="Accuracy",
            overlaying="y",
            side="right",
            range=[0, 1.05],
            showgrid=False
        ),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=900,
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.9)'
        ),
        hovermode='x unified'
    )

    return {"elbow_curve": fig.to_json()}


# Additional: KNN distance weighting visualization
def generate_knn_distance_visualization(model, X_test, y_test, sample_idx: int = 0):
    """Visualize distance weighting for a specific sample"""
    if not hasattr(model, 'predict_proba'):
        return {}
    
    # Get distances and indices for the sample
    _sample = X_test[[sample_idx]] if isinstance(X_test, np.ndarray) else X_test.iloc[[sample_idx]]
    distances, indices = model.kneighbors(_sample)
    
    fig = go.Figure()
    
    # Add bars for distances
    fig.add_trace(go.Bar(
        x=list(range(1, len(distances[0]) + 1)),
        y=distances[0],
        name="Distance",
        marker_color='#1f77b4',
        hovertemplate="Neighbor %{x}<br>Distance: %{y:.3f}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text=f"KNN Distances for Sample {sample_idx}",
            x=0.05,
            xanchor='left'
        ),
        xaxis_title="Neighbor Rank",
        yaxis_title="Distance",
        width=600,
        height=400
    )
    
    return fig.to_json()