import numpy as np
import plotly.graph_objects as go


def generate_acf_pacf_visualizations(
    acf_values: np.ndarray,
    pacf_values: np.ndarray,
    acf_confint: np.ndarray,
    pacf_confint: np.ndarray,
    nlags: int,
    alpha: float,
    series_length: int = None
) -> dict:
    """
    Generate publication-quality ACF and PACF visualizations
    
    Parameters:
    series_length: Length of the original time series (for significance level calculation)
    """
    if series_length is None:
        series_length = len(acf_values) * 5  # Reasonable estimate if not provided
    
    visuals = {}
    conf_level = int((1-alpha)*100)
    sig_level = 1.96 / np.sqrt(series_length)
    
    # Create ACF plot
    fig = go.Figure()
    
    # Add ACF values as bars with professional styling
    fig.add_trace(go.Bar(
        x=list(range(nlags+1)),
        y=acf_values,
        name="ACF",
        marker_color='#1f77b4',
        marker_line_width=0,
        width=0.7,
        opacity=0.8,
        hovertemplate='Lag: %{x}<br>ACF: %{y:.3f}<extra></extra>'
    ))
    
    # Add confidence interval as a filled area
    fig.add_trace(go.Scatter(
        x=list(range(nlags+1)),
        y=acf_confint[:, 1],  # Upper bound
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='none'
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(nlags+1)),
        y=acf_confint[:, 0],  # Lower bound
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(31, 119, 180, 0.2)',
        name=f'{conf_level}% Confidence',
        hovertemplate='Lag: %{x}<br>CI: [%{y:.3f}, %{customdata[0]:.3f}]<extra></extra>',
        customdata=acf_confint[:, 1:2]  # For hover display
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_width=1.5, line_color='#2a3f5f')
    
    # Add significance level lines
    fig.add_hline(y=sig_level, line_dash="dash", line_color="red", 
                 annotation_text=f"{conf_level}% Sig. Level", 
                 annotation_position="top right",
                 annotation_font_size=10)
    
    fig.add_hline(y=-sig_level, line_dash="dash", line_color="red")
    
    # Update layout with professional styling
    fig.update_layout(
        title=dict(text="Autocorrelation Function (ACF)", x=0.05, xanchor='left'),
        xaxis_title="Lag",
        yaxis_title="ACF Value",
        hovermode="x unified",
        showlegend=True,
        bargap=0.1,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    # Set x-axis range to start from -0.5 for better visual appearance
    fig.update_xaxes(range=[-0.5, nlags+0.5])
    
    visuals["acf_plot"] = fig.to_json()
    
    # Create PACF plot
    fig = go.Figure()
    
    # Add PACF values as bars with professional styling
    fig.add_trace(go.Bar(
        x=list(range(nlags+1)),
        y=pacf_values,
        name="PACF",
        marker_color='#2ca02c',
        marker_line_width=0,
        width=0.7,
        opacity=0.8,
        hovertemplate='Lag: %{x}<br>PACF: %{y:.3f}<extra></extra>'
    ))
    
    # Add confidence interval as a filled area
    fig.add_trace(go.Scatter(
        x=list(range(nlags+1)),
        y=pacf_confint[:, 1],  # Upper bound
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='none'
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(nlags+1)),
        y=pacf_confint[:, 0],  # Lower bound
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(44, 160, 44, 0.2)',
        name=f'{conf_level}% Confidence',
        hovertemplate='Lag: %{x}<br>CI: [%{y:.3f}, %{customdata[0]:.3f}]<extra></extra>',
        customdata=pacf_confint[:, 1:2]  # For hover display
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_width=1.5, line_color='#2a3f5f')
    
    # Add significance level lines
    fig.add_hline(y=sig_level, line_dash="dash", line_color="red", 
                 annotation_text=f"{conf_level}% Sig. Level", 
                 annotation_position="top right",
                 annotation_font_size=10)
    
    fig.add_hline(y=-sig_level, line_dash="dash", line_color="red")
    
    # Update layout with professional styling
    fig.update_layout(
        title=dict(text="Partial Autocorrelation Function (PACF)", x=0.05, xanchor='left'),
        xaxis_title="Lag",
        yaxis_title="PACF Value",
        hovermode="x unified",
        showlegend=True,
        bargap=0.1,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    # Set x-axis range to start from -0.5 for better visual appearance
    fig.update_xaxes(range=[-0.5, nlags+0.5])
    
    visuals["pacf_plot"] = fig.to_json()
    
    return visuals