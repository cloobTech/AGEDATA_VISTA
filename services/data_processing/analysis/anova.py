import statsmodels.api as sm
from statsmodels.formula.api import ols
from typing import Dict, Any
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.report import crud
from schemas.data_progressing import AnalysisInput  # Adjust import as needed


async def perform_anova(data: pd.DataFrame, input: AnalysisInput, session: AsyncSession) -> Dict[str, Any]:
    """
    Perform ANOVA analysis using StatsModels.

    :param data: Input DataFrame
    :param input: Analysis input containing parameters
    :param session: Database session
    :return: Dictionary with ANOVA results and visualizations
    """
    inputs = input.analysis_input

    # Validate required parameters
    if not hasattr(inputs, 'factor_cols') or not inputs.factor_cols:
        raise ValueError("ANOVA requires factor_cols parameter")
    if not hasattr(inputs, 'value_col') or not inputs.value_col:
        raise ValueError("ANOVA requires value_col parameter")

    # Prepare the formula for ANOVA
    formula = f"{inputs.value_col} ~ "

    # Handle different types of ANOVA
    if len(inputs.factor_cols) == 1:
        # One-way ANOVA
        formula += f"C({inputs.factor_cols[0]})"
    else:
        # Multi-way ANOVA with interactions
        factors = [f"C({factor})" for factor in inputs.factor_cols]
        formula += " + ".join(factors)

        # Add interaction terms if requested
        if getattr(inputs, 'include_interactions', False):
            formula += " + " + " + ".join([f"{factors[i]}:{factors[j]}"
                                           for i in range(len(factors))
                                           for j in range(i+1, len(factors))])

    # Fit the model
    model = ols(formula, data=data).fit()

    # Perform ANOVA
    anova_table = sm.stats.anova_lm(model, typ=2)  # Using Type II ANOVA

    # Prepare response
    response_content = {
        "anova_table": anova_table.to_dict(),
        "model_summary": str(model.summary()),
        "formula": formula,
        "residuals": model.resid.tolist(),
        "fitted_values": model.fittedvalues.tolist()
    }

    # Add effect sizes if requested
    if getattr(inputs, 'calculate_effect_sizes', False):
        effect_sizes = calculate_effect_sizes(anova_table, model)
        response_content["effect_sizes"] = effect_sizes

    # Create report object (similar to your regression function)
    report_obj = {
        "visualizations": {},  # You can add ANOVA visualizations here
        'project_id': input.project_id,
        'summary': response_content,
        'title': input.title,
        'analysis_group': input.analysis_group
    }

    # Create and store report if needed
    report = await crud.create_report(report_obj, session=session)
    return report


def calculate_effect_sizes(anova_table, model) -> Dict[str, float]:
    """
    Calculate effect sizes (eta squared) for ANOVA results.
    """
    effect_sizes = {}
    total_ss = anova_table['sum_sq'].sum()

    for factor in anova_table.index:
        if factor != 'Residual':
            effect_sizes[f"{factor}_eta_sq"] = anova_table.loc[factor,
                                                               'sum_sq'] / total_ss

    return effect_sizes
