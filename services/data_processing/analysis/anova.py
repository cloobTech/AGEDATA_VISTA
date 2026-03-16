import statsmodels.api as sm
from statsmodels.formula.api import ols
from typing import Dict, Any
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from scipy.stats import levene, shapiro
from services.data_processing.report import crud
from services.data_processing.visualization.anova import generate_anova_visualizations
from schemas.data_processing import AnalysisInput  # Adjust import as needed


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

    # Validate group sizes
    for factor in inputs.factor_cols:
        if factor in data.columns:
            group_counts = data.groupby(factor).size()
            small_groups = group_counts[group_counts < 2]
            if not small_groups.empty:
                raise ValueError(
                    f"Factor '{factor}' has groups with fewer than 2 observations: "
                    f"{small_groups.to_dict()}. Each group needs at least 2 samples for ANOVA."
                )

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

    # Levene test for homogeneity of variance
    if len(inputs.factor_cols) == 1:
        groups = [group[inputs.value_col].dropna().values
                  for _, group in data.groupby(inputs.factor_cols[0])]
        if all(len(g) >= 2 for g in groups):
            lev_stat, lev_p = levene(*groups)
            response_content["levene_test"] = {
                "statistic": float(lev_stat),
                "p_value": float(lev_p)
            }
            if lev_p < 0.05:
                response_content["levene_warning"] = (
                    "Variance homogeneity assumption may be violated "
                    f"(Levene p={lev_p:.4f} < 0.05). Consider Welch's ANOVA."
                )

    # Shapiro-Wilk test on residuals
    if len(model.resid) >= 3:
        sw_stat, sw_p = shapiro(model.resid)
        response_content["shapiro_wilk_test"] = {
            "statistic": float(sw_stat),
            "p_value": float(sw_p)
        }
        if sw_p < 0.05:
            response_content["normality_warning"] = (
                "Residuals may not be normally distributed "
                f"(Shapiro-Wilk p={sw_p:.4f} < 0.05)."
            )

    # Add effect sizes if requested
    if getattr(inputs, 'calculate_effect_sizes', False):
        effect_sizes = calculate_effect_sizes(anova_table, model)
        response_content["effect_sizes"] = effect_sizes

    visualizations = {}

    # Generate visualization
    if input.generate_visualizations:
        visualizations = generate_anova_visualizations(
            data=data,
            model=model,
            factor_cols=inputs.factor_cols,
            value_col=inputs.value_col
        )

    # Create report object (similar to your regression function)
    report_obj = {
        "visualizations": visualizations,  # You can add ANOVA visualizations here
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
    For multi-way ANOVA, also includes partial eta squared.
    """
    effect_sizes = {}
    total_ss = anova_table['sum_sq'].sum()
    ss_residual = anova_table.loc['Residual', 'sum_sq'] if 'Residual' in anova_table.index else 1.0

    for factor in anova_table.index:
        if factor != 'Residual':
            ss_factor = anova_table.loc[factor, 'sum_sq']
            # Total eta squared (sums to <= 1)
            effect_sizes[f"{factor}_eta_sq"] = ss_factor / total_ss

    return effect_sizes
