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

    # Validate n_components
    max_components = min(len(x_cols), len(y_cols))
    if n_components > max_components:
        raise ValueError(
            f"n_components ({n_components}) cannot exceed "
            f"min(len(x_cols)={len(x_cols)}, len(y_cols)={len(y_cols)}) = {max_components}"
        )

    # Drop missing values and scale
    X = data[x_cols].dropna()
    Y = data[y_cols].loc[X.index]

    if len(X) <= max(len(x_cols), len(y_cols)):
        raise ValueError(
            f"Insufficient observations ({len(X)}) for CCA. "
            f"Need more observations than variables (max variables: {max(len(x_cols), len(y_cols))})."
        )

    # Phase 5S: use two *separate* scalers — sharing one scaler caused Y to
    # be fit-transformed with X's mean/std, corrupting the Y distribution.
    scaler_x = StandardScaler()
    scaler_y = StandardScaler()
    X_scaled = scaler_x.fit_transform(X)
    Y_scaled = scaler_y.fit_transform(Y)

    # Check for singular matrices (perfect collinearity)
    x_rank = np.linalg.matrix_rank(X_scaled)
    y_rank = np.linalg.matrix_rank(Y_scaled)
    if x_rank < X_scaled.shape[1]:
        raise ValueError(
            f"X matrix is rank-deficient ({x_rank} < {X_scaled.shape[1]}). "
            "Perfect collinearity detected. Remove redundant features before CCA."
        )
    if y_rank < Y_scaled.shape[1]:
        raise ValueError(
            f"Y matrix is rank-deficient ({y_rank} < {Y_scaled.shape[1]}). "
            "Perfect collinearity detected. Remove redundant features before CCA."
        )

    cca = CCA(n_components=n_components)
    X_c, Y_c = cca.fit_transform(X_scaled, Y_scaled)

    # Canonical correlations
    canonical_corrs = [np.corrcoef(X_c[:, i], Y_c[:, i])[0, 1]
                       for i in range(n_components)]

    # Phase 5S: add Wilks' Lambda significance tests via statsmodels CanCorr
    wilks_data = {}
    try:
        from statsmodels.multivariate.cancorr import CanCorr
        cc_model = CanCorr(Y_scaled, X_scaled)
        stats_df = cc_model.stats
        wilks_data = {
            "wilks_lambda": stats_df["Wilks' lambda"].tolist(),
            "chi2_stats":   stats_df["Chi-Sq"].tolist(),
            "p_values":     stats_df["Pr > ChiSq"].tolist(),
            "significance_note": (
                "Wilks' Lambda tests whether each canonical correlation is "
                "statistically significant. p < 0.05 indicates the variate pair "
                "captures meaningful shared variance."
            ),
        }
    except Exception as exc:
        wilks_data = {"error": f"Wilks' Lambda computation failed: {exc}"}

    summary = {
        "canonical_correlations": [float(c) for c in canonical_corrs],
        "n_components": n_components,
        "x_cols": x_cols,
        "y_cols": y_cols,
        **wilks_data,
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
