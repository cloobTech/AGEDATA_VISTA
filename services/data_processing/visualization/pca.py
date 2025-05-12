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
    Generate PCA visualizations using Plotly and export as JSON.
    """
    visuals = {}
    pc_cols = [col for col in pca_df.columns if col.startswith('PC')]
    
    # Scree plot
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"PC{i+1}" for i in range(len(pca_model.explained_variance_ratio_))],
        y=pca_model.explained_variance_ratio_,
        name="Explained Variance"
    ))
    fig.add_trace(go.Scatter(
        x=[f"PC{i+1}" for i in range(len(pca_model.explained_variance_ratio_))],
        y=np.cumsum(pca_model.explained_variance_ratio_),
        name="Cumulative Variance",
        mode='lines+markers'
    ))
    fig.update_layout(
        title="Scree Plot - Explained Variance",
        xaxis_title="Principal Components",
        yaxis_title="Explained Variance Ratio",
        hovermode="x unified"
    )
    visuals["scree_plot"] = fig.to_json()
    
    # PCA 2D plot
    if len(pc_cols) >= 2:
        hover_data = {hover_col: True} if hover_col else None
        fig = px.scatter(
            pca_df,
            x="PC1",
            y="PC2",
            color=color_col,
            hover_data=hover_data,
            title="PCA - First Two Components"
        )
        visuals["pca_2d"] = fig.to_json()
    
    # PCA 3D plot
    if len(pc_cols) >= 3:
        hover_data = {hover_col: True} if hover_col else None
        fig = px.scatter_3d(
            pca_df,
            x="PC1",
            y="PC2",
            z="PC3",
            color=color_col,
            hover_data=hover_data,
            title="PCA - First Three Components"
        )
        visuals["pca_3d"] = fig.to_json()
    
    # Loadings plot
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
                mode='lines+markers+text',
                marker=dict(size=10),
                line=dict(width=1),
                name=feature,
                text=[None, feature],
                textposition="top center"
            ))
        fig.update_layout(
            title="PCA Loadings Plot",
            xaxis_title="PC1",
            yaxis_title="PC2",
            showlegend=False
        )
        visuals["loadings_plot"] = fig.to_json()
    
    # Biplot
    if len(pc_cols) >= 2:
        fig = make_subplots()
        
        # Add scores
        color_data = pca_df[color_col] if color_col else None
        fig.add_trace(go.Scatter(
            x=pca_df["PC1"],
            y=pca_df["PC2"],
            mode='markers',
            marker=dict(
                color=color_data,
                colorscale='Viridis' if color_col else None,
                showscale=bool(color_col)
            ),
            name="Scores",
            hovertext=pca_df[hover_col] if hover_col else None,
            hoverinfo="text" if hover_col else "skip"
        ))
        
        # Add loadings with scaling
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
                marker=dict(size=8),
                line=dict(width=2),
                name=feature,
                text=[None, feature],
                textposition="top center",
                hoverinfo="name"
            ))
        
        fig.update_layout(
            title="PCA Biplot",
            xaxis_title="PC1",
            yaxis_title="PC2",
            showlegend=bool(color_col)
        )
        visuals["biplot"] = fig.to_json()
    
    return visuals