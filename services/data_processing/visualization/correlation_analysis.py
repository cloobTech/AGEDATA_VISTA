import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def generate_correlation_visualizations(corr_matrix: pd.DataFrame, numeric_cols: list) -> dict:
    """
    Generate Plotly visualizations for correlation analysis and export as JSON.
    
    :param corr_matrix: Correlation matrix DataFrame
    :param numeric_cols: List of numeric column names
    :return: Dictionary with visualization JSONs
    """
    visuals = {}
    
    # Create interactive correlation heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu',
        zmin=-1,
        zmax=1,
        hoverongaps=False,
        text=corr_matrix.values.round(2),
        texttemplate="%{text}",
        textfont={"size":10}
    ))
    
    fig.update_layout(
        title='Correlation Matrix',
        xaxis_title="Variables",
        yaxis_title="Variables",
        height=600,
        width=800
    )
    
    visuals["correlation_heatmap"] = fig.to_json()
    
    # Create scatter plot matrix if we have 5 or fewer variables
    if len(numeric_cols) <= 5:
        scatter_matrix = px.scatter_matrix(
            corr_matrix,
            dimensions=numeric_cols,
            title='Scatter Plot Matrix'
        )
        visuals["scatter_matrix"] = scatter_matrix.to_json()
    
    # Create individual scatter plots for each variable pair
    if len(numeric_cols) <= 10:  # Limit to prevent too many plots
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                x_col = numeric_cols[i]
                y_col = numeric_cols[j]
                fig = px.scatter(
                    corr_matrix,
                    x=x_col,
                    y=y_col,
                    trendline="ols",
                    title=f"{x_col} vs {y_col}"
                )
                visuals[f"scatter_{x_col}_{y_col}"] = fig.to_json()
    
    return visuals