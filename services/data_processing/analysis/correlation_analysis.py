
import pandas as pd
import numpy as np
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.report import crud
from services.data_processing.visualization.correlation_analysis import generate_correlation_visualizations
from schemas.data_processing import AnalysisInput


async def perform_correlation_analysis(data: pd.DataFrame, input: AnalysisInput, session: AsyncSession) -> Dict[str, Any]:
    """
    Perform correlation analysis on the given data with Plotly visualizations exported as JSON.

    :param data: Input DataFrame
    :param input: Analysis input containing parameters
    :param session: Database session
    :return: Dictionary with correlation results and visualizations
    """
    inputs = input.analysis_input

    # Validate required parameters
    if not hasattr(inputs, 'numeric_cols') or not inputs.numeric_cols:
        raise ValueError(
            "Correlation analysis requires numeric_cols parameter")

    # Select only numeric columns for correlation
    numeric_data = data[inputs.numeric_cols]

    # Phase 5E: disclose correlation method with methodological note
    method = getattr(inputs, 'method', 'pearson')
    corr_matrix = numeric_data.corr(method=method)

    method_notes = {
        'pearson':  'Pearson assumes bivariate normality and linear relationships.',
        'spearman': 'Spearman is rank-based and appropriate for non-normal or ordinal data.',
        'kendall':  'Kendall is robust and appropriate for small samples or many ties.',
    }

    # Prepare response
    response_content = {
        "correlation_matrix": corr_matrix.to_dict(),
        "method": method,
        "method_note": method_notes.get(method, ""),
    }

    # Phase 5F: FDR-corrected p-values + Phase 5G: NaN-safe pairwise
    if getattr(inputs, 'compute_p_values', False):
        raw_matrix, corrected_matrix = calculate_correlation_p_values_fdr(numeric_data, method)
        response_content["p_values"] = raw_matrix.to_dict()
        response_content["p_values_corrected_fdr"] = corrected_matrix.to_dict()
        response_content["correction_method"] = "Benjamini-Hochberg FDR"

    visualizations = {}

    # Generate visualization if requested
    if input.generate_visualizations:
        visualizations = generate_correlation_visualizations(
            corr_matrix=corr_matrix,
            numeric_cols=inputs.numeric_cols
        )

    # Create report object
    report_obj = {
        "visualizations": visualizations,
        'project_id': input.project_id,
        'summary': response_content,
        'title': input.title,
        'analysis_group': input.analysis_group
    }

    # Create and store report
    report = await crud.create_report(report_obj, session=session)
    return report


def calculate_correlation_p_values_fdr(
    data: pd.DataFrame, method: str = 'pearson'
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (raw_p_matrix, fdr_corrected_p_matrix) for the upper triangle.

    Phase 5F: applies Benjamini-Hochberg FDR correction across all pairwise
    p-values to control the false-discovery rate for multiple comparisons.

    Phase 5G: drops NaN rows pairwise before computing each correlation so
    missing values in one column do not inflate the pair-count.
    """
    from scipy.stats import pearsonr, spearmanr, kendalltau
    from statsmodels.stats.multitest import multipletests

    cols = list(data.columns)
    k = len(cols)

    raw = np.full((k, k), np.nan)
    np.fill_diagonal(raw, 1.0)

    pair_indices = [(i, j) for i in range(k) for j in range(i + 1, k)]
    pvals_flat: list[float] = []

    for i, j in pair_indices:
        # Phase 5G: pairwise NaN drop
        pair = data[[cols[i], cols[j]]].dropna()
        if len(pair) < 3:
            pvals_flat.append(np.nan)
            continue
        if method == 'pearson':
            _, p = pearsonr(pair.iloc[:, 0], pair.iloc[:, 1])
        elif method == 'spearman':
            _, p = spearmanr(pair.iloc[:, 0], pair.iloc[:, 1])
        elif method == 'kendall':
            _, p = kendalltau(pair.iloc[:, 0], pair.iloc[:, 1])
        else:
            raise ValueError(f"Unknown correlation method: {method}")
        pvals_flat.append(float(p))
        raw[i, j] = raw[j, i] = float(p)

    # Phase 5F: FDR correction on non-NaN p-values
    valid_mask = [not np.isnan(p) for p in pvals_flat]
    corrected_p = np.full(len(pvals_flat), np.nan)
    if sum(valid_mask) > 0:
        valid_pvals = [p for p, m in zip(pvals_flat, valid_mask) if m]
        _, pvals_corr, _, _ = multipletests(valid_pvals, method='fdr_bh')
        vi = 0
        for idx, m in enumerate(valid_mask):
            if m:
                corrected_p[idx] = pvals_corr[vi]
                vi += 1

    corrected = np.full((k, k), np.nan)
    np.fill_diagonal(corrected, 1.0)
    for idx, (i, j) in enumerate(pair_indices):
        corrected[i, j] = corrected[j, i] = corrected_p[idx]

    raw_df = pd.DataFrame(raw, index=cols, columns=cols)
    corrected_df = pd.DataFrame(corrected, index=cols, columns=cols)
    return raw_df, corrected_df
