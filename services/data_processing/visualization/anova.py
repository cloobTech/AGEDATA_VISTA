import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import scipy.stats as stats
from statsmodels.regression.linear_model import RegressionResultsWrapper


def generate_anova_visualizations(data: pd.DataFrame, model: RegressionResultsWrapper, factor_cols: list, value_col: str) -> dict:
    visuals = {}

    # Box plot for each factor
    if len(factor_cols) == 1:
        fig = px.box(data, x=factor_cols[0], y=value_col, color=factor_cols[0],
                     title=f"{value_col} by {factor_cols[0]}", points="all")
        visuals["box_plot"] = fig.to_json()
    elif len(factor_cols) >= 2:
        fig = px.box(data, x=factor_cols[0], y=value_col, color=factor_cols[1],
                     title=f"{value_col} by {factor_cols[0]} and {factor_cols[1]}", points="all")
        visuals["box_plot"] = fig.to_json()

    # Interaction plot (only for 2+ factors)
    if len(factor_cols) >= 2:
        grouped = data.groupby([factor_cols[0], factor_cols[1]])[value_col].mean().reset_index()
        fig = go.Figure()
        for level in grouped[factor_cols[1]].unique():
            subset = grouped[grouped[factor_cols[1]] == level]
            fig.add_trace(go.Scatter(
                x=subset[factor_cols[0]], y=subset[value_col],
                mode="lines+markers", name=f"{factor_cols[1]}={level}"
            ))
        fig.update_layout(title="Interaction Plot", xaxis_title=factor_cols[0], yaxis_title=f"Mean {value_col}")
        visuals["interaction_plot"] = fig.to_json()

    # Residuals plot
    residual_df = pd.DataFrame({
        "fitted": model.fittedvalues,
        "residuals": model.resid
    })
    fig = px.scatter(residual_df, x="fitted", y="residuals",
                     title="Residuals vs Fitted Values")
    fig.add_hline(y=0, line_dash="dash")
    visuals["residuals_vs_fitted"] = fig.to_json()

    # QQ plot
    sorted_resid = np.sort(model.resid)
    theoretical_q = stats.norm.ppf(np.linspace(0.01, 0.99, len(sorted_resid)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=theoretical_q, y=sorted_resid, mode="markers", name="Residuals"))
    fig.add_trace(go.Scatter(x=theoretical_q, y=theoretical_q, mode="lines", name="45-degree line"))
    fig.update_layout(title="QQ Plot", xaxis_title="Theoretical Quantiles", yaxis_title="Sample Quantiles")
    visuals["qq_plot"] = fig.to_json()

    return visuals
