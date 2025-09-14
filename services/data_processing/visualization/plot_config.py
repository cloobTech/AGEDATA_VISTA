# plotly_theme.py
import plotly.io as pio
import plotly.graph_objects as go

def register_professional_theme():
    professional_theme = go.layout.Template(
        layout=go.Layout(
            font=dict(family="Arial, sans-serif", size=12, color="#2a3f5f"),
            xaxis=dict(
                showline=True,
                linewidth=1.5,
                linecolor='#2a3f5f',
                mirror=False,
                showgrid=True,
                gridwidth=0.5,
                gridcolor='#E5ECF6',
                ticks='outside',
                tickwidth=1,
                ticklen=5,
                tickcolor='#2a3f5f',
                zeroline=False,
                title=dict(standoff=10)
            ),
            yaxis=dict(
                showline=True,
                linewidth=1.5,
                linecolor='#2a3f5f',
                mirror=False,
                showgrid=True,
                gridwidth=0.5,
                gridcolor='#E5ECF6',
                ticks='outside',
                tickwidth=1,
                ticklen=5,
                tickcolor='#2a3f5f',
                zeroline=False,
                title=dict(standoff=10)
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=80, r=50, t=80, b=80),
            width=900,
            height=500,
            autosize=False,
            title=dict(
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=18, color='#2a3f5f', family="Arial, sans-serif")
            ),
            legend=dict(
                bordercolor="#E5ECF6",
                borderwidth=1,
                bgcolor="rgba(255,255,255,0.8)",
                x=1.02,
                y=1,
                xanchor='left',
                yanchor='top',
                font=dict(size=10)
            ),
            annotationdefaults=dict(
                font=dict(size=12, color="#2a3f5f"),
                bordercolor="#E5ECF6",
                borderwidth=1,
                bgcolor="white"
            )
        )
    )

    pio.templates["professional_theme"] = professional_theme
    pio.templates.default = "professional_theme"
