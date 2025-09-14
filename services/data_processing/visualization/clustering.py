import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
import numpy as np


def generate_cluster_visualizations(cluster_df: pd.DataFrame,
                                   features: list,
                                   color_col: str = None,
                                   hover_col: str = None) -> dict:
    visuals = {}

    # Reduce to 2D for visualization using PCA
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(cluster_df[features])
    viz_df = pd.DataFrame(reduced, columns=["PC1", "PC2"])
    viz_df["Cluster"] = cluster_df["Cluster"]

    if color_col in cluster_df.columns:
        viz_df[color_col] = cluster_df[color_col]
    if hover_col in cluster_df.columns:
        viz_df[hover_col] = cluster_df[hover_col]

    # Calculate variance explained
    variance_explained = pca.explained_variance_ratio_
    
    # 2D Scatter plot with professional styling
    hover_data = {hover_col: True} if hover_col else None
    
    # Use Plotly's qualitative color sequence for clusters
    fig = px.scatter(
        viz_df,
        x="PC1",
        y="PC2",
        color="Cluster",
        hover_data=hover_data,
        title=f"Cluster Visualization - PCA 2D (Variance Explained: {variance_explained[0]:.1%}, {variance_explained[1]:.1%})",
        color_discrete_sequence=px.colors.qualitative.Plotly,
        opacity=0.8
    )
    
    # Apply professional styling
    fig.update_layout(
        title=dict(
            text=f"Cluster Visualization - PCA 2D<br><sup>Variance Explained: PC1: {variance_explained[0]:.1%}, PC2: {variance_explained[1]:.1%}</sup>",
            x=0.05,
            xanchor='left',
            font=dict(size=18, color='#2a3f5f')
        ),
        xaxis_title=f"Principal Component 1 ({variance_explained[0]:.1%} variance)",
        yaxis_title=f"Principal Component 2 ({variance_explained[1]:.1%} variance)",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f',
            showline=True,
            linewidth=2,
            linecolor='#2a3f5f'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f',
            showline=True,
            linewidth=2,
            linecolor='#2a3f5f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=900,
        height=700,
        hovermode='closest',
        legend=dict(
            title=dict(text='Cluster'),
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#E5ECF6',
            borderwidth=1,
            font=dict(size=12)
        )
    )
    
    # Enhance marker styling
    fig.update_traces(
        marker=dict(
            size=10,
            opacity=0.8,
            line=dict(
                width=1.5,
                color='DarkSlateGrey'
            )
        ),
        selector=dict(mode='markers')
    )
    
    # Add cluster centroids
    centroids = viz_df.groupby('Cluster')[['PC1', 'PC2']].mean()
    for cluster_id in centroids.index:
        fig.add_trace(go.Scatter(
            x=[centroids.loc[cluster_id, 'PC1']],
            y=[centroids.loc[cluster_id, 'PC2']],
            mode='markers',
            marker=dict(
                symbol='x',
                size=15,
                color='black',
                line=dict(width=3)
            ),
            name=f'Cluster {cluster_id} Centroid',
            showlegend=False,
            hoverinfo='skip'
        ))

    visuals["cluster_2d"] = fig.to_json()
    
    # Additional visualization: 3D PCA if you want to add it later
    # visuals["cluster_3d"] = generate_3d_cluster_visualization(cluster_df, features)

    return visuals