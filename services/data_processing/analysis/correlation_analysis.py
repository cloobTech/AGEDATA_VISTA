
import pandas as pd
import numpy as np
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.report import crud
from services.data_processing.visualization.correlation_analysis import generate_correlation_visualizations
from schemas.data_progressing import AnalysisInput


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

    # Calculate correlation matrix
    method = getattr(inputs, 'method', 'pearson')
    corr_matrix = numeric_data.corr(method=method)

    # Prepare response
    response_content = {
        "correlation_matrix": corr_matrix.to_dict(),
        "method": method
    }

    # Calculate p-values if requested
    if getattr(inputs, 'compute_p_values', False):
        p_values = calculate_correlation_p_values(numeric_data, method)
        response_content["p_values"] = p_values.to_dict()

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


def calculate_correlation_p_values(data: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
    """
    Calculate p-values for correlation coefficients.

    :param data: Input DataFrame with numeric columns
    :param method: Correlation method ('pearson', 'spearman', 'kendall')
    :return: DataFrame with p-values
    """
    from scipy.stats import pearsonr, spearmanr, kendalltau

    cols = data.columns
    n = len(cols)
    p_values = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i == j:
                p_values[i, j] = 0  # Diagonal is 1.0 correlation with itself
            else:
                if method == 'pearson':
                    _, p_val = pearsonr(data[cols[i]], data[cols[j]])
                elif method == 'spearman':
                    _, p_val = spearmanr(data[cols[i]], data[cols[j]])
                elif method == 'kendall':
                    _, p_val = kendalltau(data[cols[i]], data[cols[j]])
                else:
                    raise ValueError(f"Unknown correlation method: {method}")
                p_values[i, j] = p_val

    return pd.DataFrame(p_values, index=cols, columns=cols)
