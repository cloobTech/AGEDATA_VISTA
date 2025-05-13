from statsmodels.tsa.stattools import acf
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def generate_acf_plot(residuals, lags=40, title="Residuals ACF Plot"):
    """
    Generate ACF plot directly with Plotly.

    :param residuals: Residual values from decomposition
    :param lags: Number of lags to show
    :param title: Plot title
    :return: Plotly Figure as JSON
    """
    # Calculate ACF and confidence intervals
    acf_values, confint = acf(
        residuals.dropna(),
        nlags=lags,
        fft=True,
        alpha=0.05
    )

    # Create the plot
    fig = go.Figure()

    # Add ACF values as bars
    fig.add_trace(
        go.Bar(
            x=list(range(len(acf_values))),
            y=acf_values,
            name="ACF",
            marker_color='blue'
        )
    )

    # Add confidence interval
    fig.add_trace(
        go.Scatter(
            x=list(range(len(acf_values))),
            y=confint[:, 0] - acf_values,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='none'
        )
    )

    fig.add_trace(
        go.Scatter(
            x=list(range(len(acf_values))),
            y=confint[:, 1] - acf_values,
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(0, 0, 255, 0.2)',
            fill='tonexty',
            name="95% Confidence",
            hoverinfo='none'
        )
    )

    # Add zero line
    fig.add_shape(
        type="line",
        x0=-1,
        y0=0,
        x1=len(acf_values),
        y1=0,
        line=dict(color="black", width=1)
    )

    fig.update_layout(
        title=title,
        xaxis_title="Lag",
        yaxis_title="ACF",
        hovermode="x",
        showlegend=True
    )

    return fig.to_json()


def generate_decomposition_visualizations(
    decomposition,
    model_type: str = "additive",
    show_observed: bool = True,
    show_trend: bool = True,
    show_seasonal: bool = True,
    show_resid: bool = True
) -> dict:
    """
    Generate time series decomposition visualizations using Plotly.
    """
    visuals = {}

    # Create main decomposition plot
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=["Observed", "Trend", "Seasonal", "Residuals"]
    )

    # Add components if they should be shown
    if show_observed and decomposition.observed is not None:
        fig.add_trace(
            go.Scatter(
                x=decomposition.observed.index,
                y=decomposition.observed,
                name="Observed",
                line=dict(color='blue')
            ),
            row=1, col=1
        )

    if show_trend and decomposition.trend is not None:
        fig.add_trace(
            go.Scatter(
                x=decomposition.trend.index,
                y=decomposition.trend,
                name="Trend",
                line=dict(color='red')
            ),
            row=2, col=1
        )

    if show_seasonal and decomposition.seasonal is not None:
        fig.add_trace(
            go.Scatter(
                x=decomposition.seasonal.index,
                y=decomposition.seasonal,
                name="Seasonal",
                line=dict(color='green')
            ),
            row=3, col=1
        )

    if show_resid and decomposition.resid is not None:
        fig.add_trace(
            go.Scatter(
                x=decomposition.resid.index,
                y=decomposition.resid,
                name="Residual",
                line=dict(color='purple'),
                mode='markers'
            ),
            row=4, col=1
        )

    fig.update_layout(
        height=800,
        title_text=f"Time Series Decomposition ({model_type} model)",
        showlegend=False
    )

    visuals["decomposition_plot"] = fig.to_json()

    # Create residual diagnostics plots
    if decomposition.resid is not None:
        # Residuals histogram (Plotly version)
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=decomposition.resid.dropna(),
            nbinsx=50,
            name="Residuals",
            marker_color='purple'
        ))
        fig.update_layout(
            title="Residuals Distribution",
            xaxis_title="Residual Value",
            yaxis_title="Count"
        )
        visuals["residuals_histogram"] = fig.to_json()

        # ACF plot of residuals (Pure Plotly version)
        if len(decomposition.resid.dropna()) > 40:  # Only plot if enough data
            visuals["residuals_acf"] = generate_acf_plot(
                decomposition.resid,
                lags=min(40, len(decomposition.resid)//2),
                title="Residuals ACF Plot"
            )

    return visuals
