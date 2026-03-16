import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def generate_correlation_visualizations(corr_matrix: pd.DataFrame, numeric_cols: list) -> dict:
    """
    Generate Plotly visualizations for correlation analysis and export as JSON.
    
    :param corr_matrix: Correlation matrix DataFrame
    :param numeric_cols: List of numeric column names
    :return: Dictionary with visualization JSONs
    """
    visuals = {}
    
    # Create interactive correlation heatmap with professional styling
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale='RdBu_r',  # Reversed for better interpretation (blue = positive)
        zmin=-1,
        zmax=1,
        hoverongaps=False,
        text=corr_matrix.values.round(3),  # 3 decimal places for precision
        texttemplate="%{text}",
        textfont={"size": 10, "color": "black"},
        hovertemplate=(
            "<b>X:</b> %{x}<br>" +
            "<b>Y:</b> %{y}<br>" +
            "<b>Correlation:</b> %{z:.3f}<br>" +
            "<extra></extra>"
        )
    ))
    
    fig.update_layout(
        title=dict(
            text="Correlation Matrix Heatmap",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="Variables",
        yaxis_title="Variables",
        xaxis=dict(
            tickangle=45,
            tickfont=dict(size=10),
            showgrid=False
        ),
        yaxis=dict(
            tickfont=dict(size=10),
            showgrid=False
        ),
        height=700,
        width=900,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=80, r=50, t=80, b=120),
        annotations=[dict(
            text="Blue: Positive Correlation | Red: Negative Correlation",
            xref="paper", yref="paper",
            x=0.5, y=-0.15,
            showarrow=False,
            font=dict(size=12, color='#666666'),
            xanchor='center'
        )]
    )
    
    # Add colorbar title
    fig.update_coloraxes(colorbar=dict(
        title=dict(text="Correlation", side="right"),
        tickvals=[-1, -0.5, 0, 0.5, 1],
        ticktext=["-1.0", "-0.5", "0", "0.5", "1.0"]
    ))
    
    visuals["correlation_heatmap"] = fig.to_json()
    
    # Create scatter plot matrix if we have 5 or fewer variables
    if len(numeric_cols) <= 5:
        scatter_matrix = px.scatter_matrix(
            corr_matrix,
            dimensions=numeric_cols,
            title='Scatter Plot Matrix',
            color_discrete_sequence=['#1f77b4'],
            opacity=0.7
        )
        
        scatter_matrix.update_layout(
            title=dict(
                text="Scatter Plot Matrix",
                x=0.05,
                xanchor='left',
                font=dict(size=18, color='#2a3f5f')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=800,
            width=800
        )
        
        # Style the scatter matrix
        scatter_matrix.update_traces(
            marker=dict(
                size=6,
                opacity=0.7,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            diagonal_visible=False,
            showupperhalf=False  # Remove upper triangle to avoid redundancy
        )
        
        visuals["scatter_matrix"] = scatter_matrix.to_json()
    
    # Create individual scatter plots for top correlations only
    if len(numeric_cols) <= 8:  # Slightly more restrictive limit
        # Get top correlations (absolute value)
        corr_pairs = []
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                x_col = numeric_cols[i]
                y_col = numeric_cols[j]
                corr_value = corr_matrix.loc[x_col, y_col]
                corr_pairs.append((x_col, y_col, abs(corr_value)))
        
        # Sort by absolute correlation and take top 12
        corr_pairs.sort(key=lambda x: x[2], reverse=True)
        top_pairs = corr_pairs[:12]
        
        for x_col, y_col, abs_corr in top_pairs:
            corr_value = corr_matrix.loc[x_col, y_col]
            
            fig = px.scatter(
                corr_matrix,
                x=x_col,
                y=y_col,
                trendline="ols",
                title=f"{x_col} vs {y_col} (r = {corr_value:.3f})",
                color_discrete_sequence=['#1f77b4'],
                opacity=0.7
            )
            
            fig.update_layout(
                title=dict(
                    text=f"{x_col} vs {y_col}<br><sup>Correlation: {corr_value:.3f}</sup>",
                    x=0.05,
                    xanchor='left',
                    font=dict(size=16, color='#2a3f5f')
                ),
                xaxis_title=x_col,
                yaxis_title=y_col,
                plot_bgcolor='white',
                paper_bgcolor='white',
                width=500,
                height=500,
                showlegend=False
            )
            
            fig.update_traces(
                marker=dict(
                    size=8,
                    opacity=0.7,
                    line=dict(width=1, color='DarkSlateGrey')
                )
            )
            
            # Style the trendline
            fig.update_traces(
                selector=dict(mode='lines'),
                line=dict(
                    color='red',
                    width=2.5,
                    dash='dash'
                )
            )
            
            visuals[f"scatter_{x_col}_{y_col}"] = fig.to_json()
    
    return visuals
