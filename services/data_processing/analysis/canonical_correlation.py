from sklearn.cross_decomposition import CCA
from sklearn.preprocessing import StandardScaler
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from typing import Dict, Any
import numpy as np
from services.data_processing.report import crud
from services.data_processing.visualization.canonical_correlation import generate_cca_scatter
from schemas.data_processing import AnalysisInput


async def perform_cca_analysis(data: pd.DataFrame, input: AnalysisInput, session: AsyncSession) -> Dict[str, Any]:
    """
    Perform Canonical Correlation Analysis (CCA) and generate results.
    """
    inputs = input.analysis_input

    x_cols = inputs.x_cols
    y_cols = inputs.y_cols
    n_components = inputs.n_components

    if not x_cols or not y_cols:
        raise ValueError("CCA requires 'x_cols' and 'y_cols'")

    # Drop missing values and scale
    X = data[x_cols].dropna()
    Y = data[y_cols].loc[X.index]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    Y_scaled = scaler.fit_transform(Y)

    cca = CCA(n_components=n_components)
    X_c, Y_c = cca.fit_transform(X_scaled, Y_scaled)

    # Canonical correlations
    canonical_corrs = [np.corrcoef(X_c[:, i], Y_c[:, i])[0, 1]
                       for i in range(n_components)]

    summary = {
        "canonical_correlations": [float(c) for c in canonical_corrs],
        "n_components": n_components,
        "x_cols": x_cols,
        "y_cols": y_cols
    }

    visualizations = {}
    if input.generate_visualizations:
        visualizations["cca_scatter"] = generate_cca_scatter(X_c, Y_c)

    report_obj = {
        "visualizations": visualizations,
        "project_id": input.project_id,
        "summary": summary,
        "title": input.title,
        "analysis_group": input.analysis_group
    }

    report = await crud.create_report(report_obj, session=session)
    return report
