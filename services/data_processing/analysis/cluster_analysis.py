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

    # Validate n_clusters
    if inputs.n_clusters < 2:
        raise ValueError(f"n_clusters must be >= 2, got {inputs.n_clusters}")
    if inputs.n_clusters >= len(X):
        raise ValueError(
            f"n_clusters ({inputs.n_clusters}) must be less than "
            f"number of samples ({len(X)})"
        )

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

    if inputs.color_col and inputs.color_col in data.columns:
        cluster_df[inputs.color_col] = data[inputs.color_col].values
    if inputs.hover_col and inputs.hover_col in data.columns:
        cluster_df[inputs.hover_col] = data[inputs.hover_col].values

    from sklearn.metrics import (
        silhouette_score as _silhouette_score,
        calinski_harabasz_score as _ch_score,
        davies_bouldin_score as _db_score,
    )

    # Phase 5O: always report the full trio of cluster validity indices.
    # Silhouette alone is insufficient — CH and DB capture different aspects:
    #   Silhouette: how similar each point is to its own cluster vs others.
    #   Calinski-Harabasz (higher = better): ratio of between-cluster to within-cluster dispersion.
    #   Davies-Bouldin (lower = better): average cluster similarity ratio.
    validity_indices = {
        "silhouette":         float(_silhouette_score(X_scaled, cluster_labels)),
        "calinski_harabasz":  float(_ch_score(X_scaled, cluster_labels)),
        "davies_bouldin":     float(_db_score(X_scaled, cluster_labels)),
    }
    if hasattr(model, "cluster_centers_"):
        validity_indices["centroids"] = model.cluster_centers_.tolist()

    # Phase 5O: optional k-optimisation sweep (KMeans only, 2..10)
    k_optimization = None
    if inputs.method == "kmeans" and getattr(inputs, "run_k_optimization", False):
        inertias, sil_scores, ch_scores, db_scores = [], [], [], []
        k_range = list(range(2, min(11, len(X))))
        for k in k_range:
            km_k = KMeans(n_clusters=k, random_state=42, n_init=10)
            lbl_k = km_k.fit_predict(X_scaled)
            inertias.append(float(km_k.inertia_))
            sil_scores.append(float(_silhouette_score(X_scaled, lbl_k)))
            ch_scores.append(float(_ch_score(X_scaled, lbl_k)))
            db_scores.append(float(_db_score(X_scaled, lbl_k)))
        k_optimization = {
            "k_range":          k_range,
            "inertia":          inertias,
            "silhouette":       sil_scores,
            "calinski_harabasz": ch_scores,
            "davies_bouldin":   db_scores,
        }

    response_content = {
        "method": inputs.method,
        "n_clusters": int(inputs.n_clusters),
        "linkage": getattr(inputs, "linkage", None),
        "cluster_counts": {
            int(k): int(v) for k, v in pd.Series(cluster_labels).value_counts().items()
        },
        "validity_indices": validity_indices,
        # keep silhouette_score at top level for backward compat
        "silhouette_score": validity_indices["silhouette"],
    }
    if k_optimization:
        response_content["k_optimization"] = k_optimization


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
