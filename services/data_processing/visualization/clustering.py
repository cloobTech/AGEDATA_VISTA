import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA


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

    # 2D Scatter plot
    hover_data = {hover_col: True} if hover_col else None
    fig = px.scatter(
        viz_df,
        x="PC1",
        y="PC2",
        color="Cluster",
        hover_data=hover_data,
        title="Cluster Visualization (PCA 2D)"
    )
    visuals["cluster_2d"] = fig.to_json()

    return visuals
