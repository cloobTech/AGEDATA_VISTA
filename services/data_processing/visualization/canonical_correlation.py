import plotly.express as px
import pandas as pd


def generate_cca_scatter(X_c, Y_c):
    df = pd.DataFrame({
        "X_c1": X_c[:, 0],
        "Y_c1": Y_c[:, 0]
    })

    fig = px.scatter(df, x="X_c1", y="Y_c1", title="Canonical Variables Scatter Plot (First Component)",
                     labels={"X_c1": "Canonical X₁", "Y_c1": "Canonical Y₁"})
    return fig.to_json()
