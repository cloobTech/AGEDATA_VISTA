from sklearn.decomposition import PCA
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def generate_pca_visualizations(pca_df: pd.DataFrame, 
                              pca_model: PCA,
                              feature_names: list,
                              color_col: str = None,
                              hover_col: str = None) -> dict:
    """
    Generate professional PCA visualizations using Plotly and export as JSON.
    """
    visuals = {}
    pc_cols = [col for col in pca_df.columns if col.startswith('PC')]
    
    # Calculate variance explained
    variance_ratio = pca_model.explained_variance_ratio_
    cumulative_variance = np.cumsum(variance_ratio)
    
    # Scree plot with professional styling
    fig = go.Figure()
    
    # Individual variance bars
    fig.add_trace(go.Bar(
        x=[f"PC{i+1}" for i in range(len(variance_ratio))],
        y=variance_ratio,
        name="Explained Variance",
        marker_color='#1f77b4',
        marker_line_width=0,
        hovertemplate="PC: %{x}<br>Variance: %{y:.3f}<extra></extra>"
    ))
    
    # Cumulative variance line
    fig.add_trace(go.Scatter(
        x=[f"PC{i+1}" for i in range(len(variance_ratio))],
        y=cumulative_variance,
        name="Cumulative Variance",
        mode='lines+markers',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=8),
        hovertemplate="PC: %{x}<br>Cumulative: %{y:.3f}<extra></extra>",
        yaxis="y2"
    ))
    
    # Add variance threshold lines (optional)
    for threshold in [0.8, 0.9, 0.95]:
        if cumulative_variance[-1] >= threshold:
            fig.add_hline(
                y=threshold, 
                line_dash="dash", 
                line_color="red",
                line_width=1.5,
                annotation_text=f"{threshold*100:.0f}% Variance",
                annotation_position="right"
            )
    
    fig.update_layout(
        title=dict(
            text="PCA Scree Plot - Explained Variance",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="Principal Components",
        yaxis_title="Explained Variance Ratio",
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f',
            range=[0, max(variance_ratio) * 1.1]
        ),
        yaxis2=dict(
            title="Cumulative Variance Ratio",
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
        hovermode="x unified",
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
        )
    )
    
    # Add annotation with total variance explained
    total_variance = cumulative_variance[-1] if len(cumulative_variance) > 0 else 0
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.98, y=0.02,
        text=f"Total Variance: {total_variance:.1%}",
        showarrow=False,
        font=dict(size=12, color="#666666"),
        bgcolor="rgba(255, 255, 255, 0.8)"
    )
    
    visuals["scree_plot"] = fig.to_json()
    
    # PCA 2D plot with professional styling
    if len(pc_cols) >= 2:
        hover_data = {hover_col: True} if hover_col else None
        
        # Get variance explained for axis labels
        pc1_var = variance_ratio[0] * 100
        pc2_var = variance_ratio[1] * 100
        
        fig = px.scatter(
            pca_df,
            x="PC1",
            y="PC2",
            color=color_col,
            hover_data=hover_data,
            title=f"PCA 2D - PC1 ({pc1_var:.1f}%) vs PC2 ({pc2_var:.1f}%)",
            color_discrete_sequence=px.colors.qualitative.Plotly,
            opacity=0.8
        )
        
        fig.update_layout(
            title=dict(
                text=f"PCA 2D - PC1 ({pc1_var:.1f}%) vs PC2 ({pc2_var:.1f}%)",
                x=0.05,
                xanchor='left',
                font=dict(size=18, color='#2a3f5f')
            ),
            xaxis_title=f"PC1 ({pc1_var:.1f}% variance)",
            yaxis_title=f"PC2 ({pc2_var:.1f}% variance)",
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
            width=800,
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
        
        fig.update_traces(
            marker=dict(size=8, line=dict(width=1, color='DarkSlateGrey')),
            selector=dict(mode='markers')
        )
        
        visuals["pca_2d"] = fig.to_json()
    
    # PCA 3D plot with professional styling
    if len(pc_cols) >= 3:
        hover_data = {hover_col: True} if hover_col else None
        
        # Get variance explained for axis labels
        pc3_var = variance_ratio[2] * 100
        
        fig = px.scatter_3d(
            pca_df,
            x="PC1",
            y="PC2",
            z="PC3",
            color=color_col,
            hover_data=hover_data,
            title=f"PCA 3D - PC1 ({pc1_var:.1f}%) vs PC2 ({pc2_var:.1f}%) vs PC3 ({pc3_var:.1f}%)",
            color_discrete_sequence=px.colors.qualitative.Plotly,
            opacity=0.8
        )
        
        fig.update_layout(
            title=dict(
                text=f"PCA 3D - First Three Components",
                x=0.05,
                xanchor='left',
                font=dict(size=18, color='#2a3f5f')
            ),
            scene=dict(
                xaxis_title=f"PC1 ({pc1_var:.1f}%)",
                yaxis_title=f"PC2 ({pc2_var:.1f}%)",
                zaxis_title=f"PC3 ({pc3_var:.1f}%)",
                bgcolor='white',
                xaxis=dict(
                    gridcolor='#E5ECF6',
                    zerolinecolor='#2a3f5f'
                ),
                yaxis=dict(
                    gridcolor='#E5ECF6',
                    zerolinecolor='#2a3f5f'
                ),
                zaxis=dict(
                    gridcolor='#E5ECF6',
                    zerolinecolor='#2a3f5f'
                )
            ),
            width=900,
            height=700,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        visuals["pca_3d"] = fig.to_json()
    
    # Loadings plot with professional styling
    if len(pc_cols) >= 2:
        loadings = pca_model.components_.T * np.sqrt(pca_model.explained_variance_)
        loadings_df = pd.DataFrame(loadings[:, :2], 
                                 columns=['PC1', 'PC2'],
                                 index=feature_names)
        
        fig = go.Figure()
        
        for i, feature in enumerate(feature_names):
            fig.add_trace(go.Scatter(
                x=[0, loadings_df.loc[feature, 'PC1']],
                y=[0, loadings_df.loc[feature, 'PC2']],
                mode='lines+markers',
                marker=dict(size=8, color='#2ca02c'),
                line=dict(width=2, color='#2ca02c'),
                name=feature,
                text=feature,
                textposition="top center",
                hovertemplate=f"Feature: {feature}<br>PC1: %{{x:.3f}}<br>PC2: %{{y:.3f}}<extra></extra>"
            ))
        
        # Add unit circle for reference
        theta = np.linspace(0, 2*np.pi, 100)
        fig.add_trace(go.Scatter(
            x=np.cos(theta),
            y=np.sin(theta),
            mode='lines',
            line=dict(color='red', dash='dash', width=1),
            name='Unit Circle',
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            title=dict(
                text="PCA Loadings Plot",
                x=0.05,
                xanchor='left',
                font=dict(size=20, color='#2a3f5f')
            ),
            xaxis_title=f"PC1 ({pc1_var:.1f}% variance)",
            yaxis_title=f"PC2 ({pc2_var:.1f}% variance)",
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
            width=800,
            height=600,
            showlegend=False,
            hovermode='closest'
        )
        
        visuals["loadings_plot"] = fig.to_json()
    
    # Biplot with professional styling
    if len(pc_cols) >= 2:
        fig = go.Figure()
        
        # Add scores with professional styling
        fig.add_trace(go.Scatter(
            x=pca_df["PC1"],
            y=pca_df["PC2"],
            mode='markers',
            marker=dict(
                color=pca_df[color_col] if color_col else '#1f77b4',
                colorscale='Viridis' if color_col else None,
                size=8,
                opacity=0.7,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            name="Scores",
            hovertext=pca_df[hover_col] if hover_col else None,
            hoverinfo="text" if hover_col else "skip",
            showlegend=bool(color_col)
        ))
        
        # Add loadings with scaling and professional styling
        scaling_factor = 0.2 * max(abs(pca_df["PC1"].max()), 
                                 abs(pca_df["PC1"].min()),
                                 abs(pca_df["PC2"].max()),
                                 abs(pca_df["PC2"].min()))
        loadings = pca_model.components_.T * scaling_factor
        
        for i, feature in enumerate(feature_names):
            fig.add_trace(go.Scatter(
                x=[0, loadings[i, 0]],
                y=[0, loadings[i, 1]],
                mode='lines+markers+text',
                marker=dict(size=8, color='#ff7f0e'),
                line=dict(width=2, color='#ff7f0e'),
                name=feature,
                text=[None, feature],
                textposition="top center",
                hoverinfo="name",
                showlegend=False
            ))
        
        fig.update_layout(
            title=dict(
                text="PCA Biplot - Scores and Loadings",
                x=0.05,
                xanchor='left',
                font=dict(size=20, color='#2a3f5f')
            ),
            xaxis_title=f"PC1 ({pc1_var:.1f}% variance)",
            yaxis_title=f"PC2 ({pc2_var:.1f}% variance)",
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
            width=900,
            height=600,
            hovermode='closest'
        )
        
        visuals["biplot"] = fig.to_json()
    
    return visuals


# Additional: PCA variance table
def generate_pca_variance_table(pca_model: PCA) -> str:
    """Generate a professional variance explanation table"""
    variance_ratio = pca_model.explained_variance_ratio_
    cumulative_variance = np.cumsum(variance_ratio)
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Component', 'Explained Variance', 'Cumulative Variance'],
            fill_color='#2a3f5f',
            font=dict(color='white', size=12),
            align='left'
        ),
        cells=dict(
            values=[
                [f"PC{i+1}" for i in range(len(variance_ratio))],
                [f"{v:.3f}" for v in variance_ratio],
                [f"{v:.3f}" for v in cumulative_variance]
            ],
            fill_color='white',
            font=dict(color='#2a3f5f', size=11),
            align='left'
        )
    )])
    
    fig.update_layout(
        title=dict(
            text="PCA Variance Explanation",
            x=0.05,
            xanchor='left'
        ),
        width=600,
        height=400
    )
    
    return fig.to_json()