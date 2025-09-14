import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np


def generate_cca_scatter(X_c, Y_c):
    df = pd.DataFrame({
        "X_c1": X_c[:, 0],
        "Y_c1": Y_c[:, 0]
    })

    # Create the scatter plot with professional styling
    fig = px.scatter(
        df, 
        x="X_c1", 
        y="Y_c1", 
        title="Canonical Correlation Analysis - First Component",
        labels={"X_c1": "First Canonical Variable (X)", "Y_c1": "First Canonical Variable (Y)"},
        opacity=0.7,
        color_discrete_sequence=['#1f77b4']  # Professional blue
    )
    
    # Add professional styling enhancements
    fig.update_layout(
        title=dict(
            text="Canonical Correlation Analysis - First Component",
            x=0.05,
            xanchor='left',
            font=dict(size=20, color='#2a3f5f')
        ),
        xaxis_title="First Canonical Variable (X)",
        yaxis_title="First Canonical Variable (Y)",
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#E5ECF6',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#2a3f5f'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=800,
        height=600,
        showlegend=False,
        hovermode='closest'
    )
    
    # Enhance marker styling
    fig.update_traces(
        marker=dict(
            size=8,
            opacity=0.7,
            line=dict(
                width=1,
                color='DarkSlateGrey'
            )
        ),
        selector=dict(mode='markers')
    )
    
    # Add correlation line if desired (optional)
    if len(df) > 1:
        # Calculate correlation line
        z = np.polyfit(df["X_c1"], df["Y_c1"], 1)
        p = np.poly1d(z)
        
        fig.add_trace(go.Scatter(
            x=df["X_c1"],
            y=p(df["X_c1"]),
            mode='lines',
            line=dict(
                color='red',
                width=2.5,
                dash='dash'
            ),
            name='Correlation Trend',
            hovertemplate='Trend Line<extra></extra>'
        ))
        
        # Update legend
        fig.update_layout(showlegend=True)
        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#E5ECF6',
            borderwidth=1
        ))

    return fig.to_json()