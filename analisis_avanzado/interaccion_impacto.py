import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from config import COLOR_PARTIDOS
from analisis_avanzado.utils import plot_top10_bar

# -------------------------------------------------------
# FUNCIONES AUXILIARES
# -------------------------------------------------------

@st.cache_data
def calcular_interaccion_promedio(df_posts: pd.DataFrame) -> pd.DataFrame:
    """
    Devuelve un DataFrame con la interacción promedio por publicación para cada político.
    """
    interacciones = (
        df_posts.groupby("ID_Político")
        .agg({
            "Likes": "sum",
            "Retweets": "sum",
            "Comentarios_Totales": "sum",
            "Enlace_Post": "count"
        })
        .rename(columns={"Enlace_Post": "Posts_extraidos"})
        .reset_index()
    )

    interacciones["Interacción"] = round(
        (interacciones["Likes"] + interacciones["Retweets"] + interacciones["Comentarios_Totales"])
        / interacciones["Posts_extraidos"],
        0
    )

    return interacciones


# -------------------------------------------------------
# FUNCIONES DE VISUALIZACIÓN
# -------------------------------------------------------

def grafico_top10_interaccion(df_metadata: pd.DataFrame, df_posts: pd.DataFrame = None) -> None:
    """
    Muestra el gráfico de los 10 políticos con mayor interacción promedio por publicación.
    Si se pasa df_posts, recalcula la interacción en tiempo real.
    """
    if df_posts is not None:
        interacciones = calcular_interaccion_promedio(df_posts)
        df = df_metadata.merge(interacciones, on="ID_Político", how="left")
    else:
        df = df_metadata.copy()

    df = df[df["Interacción"].notna()]
    top10 = df[["Nombre", "Partido", "Interacción"]].nlargest(10, "Interacción")

    fig = go.Figure()
    for partido in top10["Partido"].unique():
        datos_partido = top10[top10["Partido"] == partido]
        fig.add_trace(go.Bar(
            x=datos_partido["Nombre"],
            y=datos_partido["Interacción"],
            name=partido,
            marker_color=COLOR_PARTIDOS.get(partido, "#cccccc"),
            text=datos_partido["Interacción"],
            textposition="outside",
            width=0.7
        ))

    fig.update_layout(
        title="Top 10 políticos con mayor interacción promedio por publicación",
        xaxis=dict(
            title="Nombre del político",
            categoryorder="array",
            categoryarray=top10["Nombre"].iloc[::-1]
        ),
        yaxis_title="Interacción promedio",
        legend_title="Partido",
        width=900,
        height=600,
        margin=dict(l=20, r=20, t=60, b=100),
        showlegend=True
    )
    st.plotly_chart(fig)


def grafico_top10_interaccion_partido(df_metadata: pd.DataFrame) -> None:
    """
    Muestra el gráfico del top 10 partidos con mayor interacción promedio por publicación.
    """
    df_filtrado = df_metadata[df_metadata["Interacción"].notna()]

    top10 = (
        df_filtrado.groupby("Partido", as_index=False)["Interacción"]
        .mean()
        .round(0)
        .nlargest(10, "Interacción")
    )

    partidos = top10["Partido"].tolist()
    interacciones = top10["Interacción"].tolist()
    colores = [COLOR_PARTIDOS.get(p, "#cccccc") for p in partidos]

    fig = go.Figure([
        go.Bar(
            x=partidos,
            y=interacciones,
            marker_color=colores,
            text=interacciones,
            textposition="outside",
            width=0.7
        )
    ])
    fig.update_layout(
        title="Top 10 partidos con mayor interacción promedio por publicación",
        xaxis=dict(
            title="Partido",
            categoryorder="array",
            categoryarray=partidos[::-1]
        ),
        yaxis_title="Interacción promedio",
        width=900,
        height=600,
        margin=dict(l=20, r=20, t=60, b=100)
    )
    st.plotly_chart(fig)


def grafico_top10_interaccion_relativa_politicos(df_metadata: pd.DataFrame) -> None:
    """
    Gráfico del top 10 políticos con mayor interacción relativa (por seguidor).
    """
    df_filtrado = df_metadata[df_metadata["Interacción_Relativa"].notna()].copy()
    df_filtrado["Interacción_Relativa"] = df_filtrado["Interacción_Relativa"].round(3)

    plot_top10_bar(
        df_filtrado,
        value_col="Interacción_Relativa",
        title="Top 10 políticos con mayor interacción relativa (por seguidor)",
        yaxis_title="Interacción relativa"
    )


def grafico_top10_interaccion_relativa_partidos(df_metadata: pd.DataFrame) -> None:
    """
    Gráfico del top 10 partidos con mayor interacción relativa promedio.
    """
    df_filtrado = df_metadata[df_metadata["Interacción_Relativa"].notna()]

    top10 = (
        df_filtrado.groupby("Partido", as_index=False)["Interacción_Relativa"]
        .mean()
        .round(3)
        .nlargest(10, "Interacción_Relativa")
    )

    partidos = top10["Partido"].tolist()
    valores = top10["Interacción_Relativa"].tolist()
    colores = [COLOR_PARTIDOS.get(p, "#cccccc") for p in partidos]

    fig = go.Figure([
        go.Bar(
            x=partidos,
            y=valores,
            marker_color=colores,
            text=valores,
            textposition="outside",
            width=0.7
        )
    ])
    fig.update_layout(
        title="Top 10 partidos con mayor interacción relativa (por seguidor)",
        xaxis=dict(
            title="Partido",
            categoryorder="array",
            categoryarray=partidos[::-1]
        ),
        yaxis_title="Interacción relativa promedio",
        width=900,
        height=600,
        margin=dict(l=20, r=20, t=60, b=80)
    )
    st.plotly_chart(fig)
