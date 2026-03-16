import plotly.graph_objects as go
import pandas as pd
import numpy as np


def generate_ma_visualizations(
    original: pd.Series,
    moving_avg: pd.Series,
    ma_type: str,
    window_size: int,
    show_confidence: bool = False,
    show_residuals: bool = False
) -> dict:
    """Generate professional moving average visualizations"""
    visuals = {}

    fig = go.Figure()

    # Original series - professional styling
    fig.add_trace(go.Scatter(
        x=original.index,
        y=original,
        name="Original Series",
        line=dict(color='#1f77b4', width=1.5),  # Professional blue
        opacity=0.7,
        hovertemplate="Date: %{x}<br>Value: %{y:.3f}<extra></extra>"
    ))

    # Moving average - professional styling
    fig.add_trace(go.Scatter(
        x=moving_avg.index,
        y=moving_avg,
        name=f"{ma_type.upper()} MA (w={window_size})",
        line=dict(color='#ff7f0e', width=3),  # Professional orange
        opacity=0.9,
        hovertemplate="Date: %{x}<br>MA: %{y:.3f}<extra></extra>"
    ))

    # Add confidence bands if requested
    if show_confidence and len(moving_avg) > 0:
        # Calculate rolling standard deviation for confidence bands
        rolling_std = original.rolling(window=window_size).std()
        upper_band = moving_avg + 1.96 * rolling_std
        lower_band = moving_avg - 1.96 * rolling_std

        # Upper confidence band
        fig.add_trace(go.Scatter(
            x=upper_band.index,
            y=upper_band,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Lower confidence band with fill
        fig.add_trace(go.Scatter(
            x=lower_band.index,
            y=lower_band,
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(255, 127, 14, 0.2)',  # Orange with transparency
            name='95% Confidence Band',
            hovertemplate="Date: %{x}<br>Lower Bound: %{y:.3f}<extra></extra>"
        ))

    fig.update_layout(
        title=dict(
            text=f"{ma_type.upper()} Moving Average (Window={window_size})",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="Time",
        yaxis_title="Value",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            showline=True,
            linewidth=2,
            linecolor='#2a3f5f'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            showline=True,
            linewidth=2,
            linecolor='#2a3f5f'
        ),
        hovermode="x unified",
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=1000,
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#E5ECF6',
            borderwidth=1,
            font=dict(size=12)
        ),
        margin=dict(l=80, r=50, t=100, b=80)
    )

    # Add annotation with MA type information
    ma_info = f"{ma_type.upper()} Moving Average smoothes data using a {window_size}-period window"
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.98, y=0.02,
        text=ma_info,
        showarrow=False,
        font=dict(size=11, color="#666666"),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="#E5ECF6",
        borderwidth=1,
        xanchor='right'
    )

    visuals["moving_average_plot"] = fig.to_json()

    # Generate residuals plot if requested
    if show_residuals and len(moving_avg) > 0:
        # Calculate residuals (difference from MA)
        residuals = original - moving_avg
        residuals = residuals.dropna()  # Remove NaN values

        fig_res = go.Figure()

        # Residuals
        fig_res.add_trace(go.Scatter(
            x=residuals.index,
            y=residuals,
            mode='markers',
            name='Residuals',
            marker=dict(
                color='#2ca02c',  # Professional green
                size=6,
                opacity=0.7,
                line=dict(width=1, color='DarkSlateGrey')
            ),
            hovertemplate="Date: %{x}<br>Residual: %{y:.3f}<extra></extra>"
        ))

        # Zero reference line
        fig_res.add_hline(
            y=0,
            line_dash="dash",
            line_width=2,
            line_color='#2a3f5f',
            annotation_text="Zero Reference",
            annotation_position="top right"
        )

        # Add confidence bands (2 standard deviations)
        residual_std = np.std(residuals)
        if np.isfinite(residual_std) and residual_std > 0:
            fig_res.add_hrect(
                y0=-2*residual_std,
                y1=2*residual_std,
                fillcolor="rgba(0, 0, 0, 0.1)",
                line_width=0,
                annotation_text="±2σ",
                annotation_position="bottom right"
            )

        fig_res.update_layout(
            title=dict(
                text=f"Residuals from {ma_type.upper()} MA",
                x=0.05,
                xanchor='left',
                font=dict(size=18, color='#2a3f5f')
            ),
            xaxis_title="Time",
            yaxis_title="Residual Value",
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E5ECF6',
                showline=True,
                linewidth=2,
                linecolor='#2a3f5f'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E5ECF6',
                showline=True,
                linewidth=2,
                linecolor='#2a3f5f'
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            width=900,
            height=500,
            showlegend=False,
            hovermode="x unified"
        )

        visuals["residuals_plot"] = fig_res.to_json()

    # Generate multiple window sizes comparison if possible
    if hasattr(original, 'rolling'):
        fig_compare = go.Figure()

        # Original series
        fig_compare.add_trace(go.Scatter(
            x=original.index,
            y=original,
            name="Original",
            line=dict(color='#1f77b4', width=1),
            opacity=0.6,
            hovertemplate="Date: %{x}<br>Value: %{y:.3f}<extra></extra>"
        ))

        # Multiple window sizes for comparison
        window_sizes = [window_size // 2, window_size, window_size * 2]
        # Different colors for each MA
        colors = ['#ff7f0e', '#d62728', '#9467bd']

        for i, ws in enumerate(window_sizes):
            if ws < len(original):
                ma = original.rolling(window=ws).mean()
                fig_compare.add_trace(go.Scatter(
                    x=ma.index,
                    y=ma,
                    name=f"MA (w={ws})",
                    line=dict(color=colors[i % len(colors)], width=2.5),
                    opacity=0.9,
                    hovertemplate=f"Date: %{{x}}<br>MA (w={ws}): %{{y:.3f}}<extra></extra>"
                ))

        fig_compare.update_layout(
            title=dict(
                text=f"Moving Average Comparison - {ma_type.upper()}",
                x=0.05,
                xanchor='left',
                font=dict(size=20, color='#2a3f5f')
            ),
            xaxis_title="Time",
            yaxis_title="Value",
            plot_bgcolor='white',
            paper_bgcolor='white',
            width=1000,
            height=600,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01,
                bgcolor='rgba(255, 255, 255, 0.9)'
            ),
            hovermode="x unified"
        )

        visuals["ma_comparison_plot"] = fig_compare.to_json()

    return visuals


# Additional function for different MA types comparison
def generate_ma_type_comparison(original: pd.Series, window_size: int) -> dict:
    """Compare different types of moving averages"""
    visuals = {}

    fig = go.Figure()

    # Original series
    fig.add_trace(go.Scatter(
        x=original.index,
        y=original,
        name="Original",
        line=dict(color='#1f77b4', width=1),
        opacity=0.6,
        hovertemplate="Date: %{x}<br>Value: %{y:.3f}<extra></extra>"
    ))

    # Simple Moving Average
    sma = original.rolling(window=window_size).mean()
    fig.add_trace(go.Scatter(
        x=sma.index,
        y=sma,
        name=f"SMA ({window_size})",
        line=dict(color='#ff7f0e', width=2.5),
        hovertemplate="Date: %{x}<br>SMA: %{y:.3f}<extra></extra>"
    ))

    # Exponential Moving Average
    ema = original.ewm(span=window_size).mean()
    fig.add_trace(go.Scatter(
        x=ema.index,
        y=ema,
        name=f"EMA ({window_size})",
        line=dict(color='#d62728', width=2.5),
        hovertemplate="Date: %{x}<br>EMA: %{y:.3f}<extra></extra>"
    ))

    # Weighted Moving Average (if desired)
    # weights = np.arange(1, window_size + 1)
    # wma = original.rolling(window=window_size).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    # fig.add_trace(go.Scatter(
    #     x=wma.index,
    #     y=wma,
    #     name=f"WMA ({window_size})",
    #     line=dict(color='#9467bd', width=2.5)
    # ))

    fig.update_layout(
        title=dict(
            text=f"Moving Average Types Comparison (Window={window_size})",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="Time",
        yaxis_title="Value",
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=1000,
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.9)'
        ),
        hovermode="x unified"
    )

    visuals["ma_types_comparison"] = fig.to_json()
    return visuals
