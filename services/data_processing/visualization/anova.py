import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import scipy.stats as stats
from statsmodels.regression.linear_model import RegressionResultsWrapper
import plotly.io as pio


def generate_anova_visualizations(data: pd.DataFrame, model: RegressionResultsWrapper, factor_cols: list, value_col: str) -> dict:
    visuals = {}

    # Box plot for each factor
    if len(factor_cols) == 1:
        fig = px.box(data, x=factor_cols[0], y=value_col, color=factor_cols[0],
                     title=f"{value_col} by {factor_cols[0]}", points="all")
        # Apply additional professional styling
        fig.update_layout(
            title=dict(x=0.05, xanchor='left'),
            showlegend=False  # Often better for single factor box plots
        )
        visuals["box_plot"] = fig.to_json()
        
    elif len(factor_cols) >= 2:
        fig = px.box(data, x=factor_cols[0], y=value_col, color=factor_cols[1],
                     title=f"{value_col} by {factor_cols[0]} and {factor_cols[1]}", points="all")
        fig.update_layout(title=dict(x=0.05, xanchor='left'))
        visuals["box_plot"] = fig.to_json()

    # Interaction plot (only for 2+ factors)
    if len(factor_cols) >= 2:
        grouped = data.groupby([factor_cols[0], factor_cols[1]])[value_col].mean().reset_index()
        fig = go.Figure()
        for level in grouped[factor_cols[1]].unique():
            subset = grouped[grouped[factor_cols[1]] == level]
            fig.add_trace(go.Scatter(
                x=subset[factor_cols[0]], y=subset[value_col],
                mode="lines+markers", 
                name=f"{factor_cols[1]}={level}",
                line=dict(width=2.5),  # Thicker lines for better visibility
                marker=dict(size=8)    # Larger markers
            ))
        fig.update_layout(
            title=dict(text="Interaction Plot", x=0.05, xanchor='left'),
            xaxis_title=factor_cols[0], 
            yaxis_title=f"Mean {value_col}",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255,255,255,0.9)'
            )
        )
        visuals["interaction_plot"] = fig.to_json()

    # Residuals plot
    residual_df = pd.DataFrame({
        "fitted": model.fittedvalues,
        "residuals": model.resid
    })
    fig = px.scatter(residual_df, x="fitted", y="residuals",
                     title="Residuals vs Fitted Values",
                     opacity=0.7)  # Add some transparency
    fig.add_hline(y=0, line_dash="dash", line_width=2, line_color='#2a3f5f')
    fig.update_layout(
        title=dict(x=0.05, xanchor='left'),
        showlegend=False
    )
    visuals["residuals_vs_fitted"] = fig.to_json()

    # QQ plot - This one needs the most attention for professional styling
    sorted_resid = np.sort(model.resid)
    theoretical_q = stats.norm.ppf(np.linspace(0.01, 0.99, len(sorted_resid)))
    fig = go.Figure()
    
    # Residual points
    fig.add_trace(go.Scatter(
        x=theoretical_q, 
        y=sorted_resid, 
        mode="markers", 
        name="Residuals",
        marker=dict(
            color='#1f77b4',
            size=6,
            opacity=0.7,
            line=dict(width=1, color='DarkSlateGrey')
        )
    ))
    
    # 45-degree reference line
    fig.add_trace(go.Scatter(
        x=theoretical_q, 
        y=theoretical_q, 
        mode="lines", 
        name="Normal Reference",
        line=dict(
            color='red', 
            width=2.5,
            dash='dash'
        )
    ))
    
    fig.update_layout(
        title=dict(text="Normal Q-Q Plot", x=0.05, xanchor='left'),
        xaxis_title="Theoretical Quantiles",
        yaxis_title="Sample Quantiles",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    visuals["qq_plot"] = fig.to_json()

    return visuals