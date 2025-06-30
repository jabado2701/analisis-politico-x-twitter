import streamlit as st
import plotly.graph_objects as go
from config import COLOR_PARTIDOS
import pandas as pd

def ajustar_nombres_ccaa(
    df: pd.DataFrame,
    columna: str = "Comunidad Autónoma"
) -> pd.DataFrame:
    """
    Corrige nombres de Comunidades Autónomas para
    unificar criterios con el geojson de mapas.
    """
    df[columna] = df[columna].replace({
        "Castilla-La Mancha": "Castilla - La Mancha",
        "Islas Baleares": "Illes Balears"
    })
    return df


def plot_top10_bar(
    df: pd.DataFrame,
    value_col: str,
    title: str,
    yaxis_title: str
) -> None:
    """
    Genera un gráfico de barras top 10 con colores
    diferenciados por partido.
    """
    # obtener top 10
    top10 = df[["Nombre", "Partido", value_col]].nlargest(10, value_col)

    fig = go.Figure()

    for partido in top10["Partido"].unique():
        datos_partido = top10[top10["Partido"] == partido]
        fig.add_trace(go.Bar(
            x=datos_partido["Nombre"],
            y=datos_partido[value_col],
            name=partido,
            marker_color=COLOR_PARTIDOS.get(partido, "#cccccc"),
            text=datos_partido[value_col],
            textposition="outside",
            width=0.7
        ))

    fig.update_layout(
        title=title,
        xaxis=dict(
            title="Nombre del político",
            categoryorder="array",
            categoryarray=top10["Nombre"].iloc[::-1]
        ),
        yaxis_title=yaxis_title,
        legend_title="Partido",
        width=1000,
        height=600,
        margin=dict(l=20, r=20, t=60, b=100)
    )
    st.plotly_chart(fig)
