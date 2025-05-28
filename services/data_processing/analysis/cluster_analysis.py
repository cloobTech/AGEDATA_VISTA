from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from services.data_processing.visualization.clustering import generate_cluster_visualizations
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.report import crud
from schemas.data_processing import AnalysisInput
import pandas as pd
from typing import Dict, Any


async def perform_cluster_analysis(data: pd.DataFrame, input: AnalysisInput, session: AsyncSession) -> Dict[str, Any]:
    """
    Perform clustering analysis (KMeans or Hierarchical) and generate visualizations.
    """
    inputs = input.analysis_input

    if not hasattr(inputs, 'numeric_cols') or not inputs.numeric_cols:
        raise ValueError("Clustering requires numeric_cols parameter")

    # Prepare data
    X = data[inputs.numeric_cols].dropna()

    if getattr(inputs, 'scale_data', True):
        X_scaled = StandardScaler().fit_transform(X)
    else:
        X_scaled = X.values

    # Choose clustering method
    if inputs.method == "kmeans":
        model = KMeans(n_clusters=inputs.n_clusters, random_state=42)
    elif inputs.method == "hierarchical":
        model = AgglomerativeClustering(n_clusters=inputs.n_clusters, linkage=inputs.linkage)
    else:
        raise ValueError(f"Unsupported clustering method: {inputs.method}")

    cluster_labels = model.fit_predict(X_scaled)

    # Append cluster labels
    cluster_df = pd.DataFrame(X_scaled, columns=inputs.numeric_cols)
    cluster_df["Cluster"] = cluster_labels

    if inputs.color_col in data.columns:
        cluster_df[inputs.color_col] = data[inputs.color_col].values
    if inputs.hover_col in data.columns:
        cluster_df[inputs.hover_col] = data[inputs.hover_col].values

    response_content = {
        "method": inputs.method,
        "n_clusters": inputs.n_clusters,
        "linkage": getattr(inputs, "linkage", None),
        "cluster_counts": dict(pd.Series(cluster_labels).value_counts())
    }

    response_content = {
    "method": inputs.method,
    "n_clusters": int(inputs.n_clusters),
    "linkage": getattr(inputs, "linkage", None),
    "cluster_counts": {
        int(k): int(v) for k, v in pd.Series(cluster_labels).value_counts().items()
    }
}


    visualizations = {}
    if input.generate_visualizations:
        visualizations = generate_cluster_visualizations(
            cluster_df=cluster_df,
            features=inputs.numeric_cols,
            color_col=getattr(inputs, 'color_col', None),
            hover_col=getattr(inputs, 'hover_col', None)
        )

    report_obj = {
        "visualizations": visualizations,
        "project_id": input.project_id,
        "summary": response_content,
        "title": input.title,
        "analysis_group": input.analysis_group
    }

    report = await crud.create_report(report_obj, session=session)
    return report
