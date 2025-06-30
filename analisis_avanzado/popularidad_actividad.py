import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import COLOR_PARTIDOS
from analisis_avanzado.utils import ajustar_nombres_ccaa, plot_top10_bar

# ---------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------

def plot_top10_partidos_bar(
    df: pd.DataFrame,
    value_col: str,
    title: str,
    yaxis_title: str
) -> None:
    """
    Gráfico de barras del top 10 partidos por la métrica especificada.
    """
    top10 = (
        df.groupby("Partido", as_index=False)[value_col]
        .sum()
        .nlargest(10, value_col)
    )

    partidos = top10["Partido"].tolist()
    valores = top10[value_col].tolist()
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
        title=title,
        xaxis=dict(
            title="Partido",
            categoryorder="array",
            categoryarray=partidos[::-1]
        ),
        yaxis_title=yaxis_title,
        width=900,
        height=600,
        margin=dict(l=20, r=20, t=60, b=80),
        showlegend=False
    )
    st.plotly_chart(fig)

@st.cache_data
def calcular_tasa_publicacion(df: pd.DataFrame, año_actual: int = 2025) -> pd.DataFrame:
    """
    Calcula la tasa de publicaciones anuales para cada político.
    """
    df = df.copy()
    df["Tasa_Posts_Año"] = df.apply(
        lambda row: round(
            row["Posts"] / (año_actual - row["Comienzo en X/Twitter"]), 0
        ) if row["Comienzo en X/Twitter"] and (año_actual - row["Comienzo en X/Twitter"]) > 0 else 0,
        axis=1
    )
    return df

# ---------------------------------------------------------
# FUNCIONES DE VISUALIZACIÓN
# ---------------------------------------------------------

def grafico_top10_politicos_seguidores(df: pd.DataFrame) -> None:
    plot_top10_bar(
        df,
        value_col="Seguidores",
        title="Top 10 políticos con más seguidores",
        yaxis_title="Seguidores"
    )

def grafico_top10_politicos_posts(df: pd.DataFrame) -> None:
    plot_top10_bar(
        df,
        value_col="Posts",
        title="Top 10 políticos con más publicaciones",
        yaxis_title="Posts"
    )

def grafico_top10_partidos_seguidores(df: pd.DataFrame) -> None:
    plot_top10_partidos_bar(
        df,
        value_col="Seguidores",
        title="Top 10 partidos con más seguidores",
        yaxis_title="Seguidores"
    )

def grafico_top10_partidos_posts(df: pd.DataFrame) -> None:
    plot_top10_partidos_bar(
        df,
        value_col="Posts",
        title="Top 10 partidos con más publicaciones",
        yaxis_title="Posts"
    )

def grafico_top10_tasa_posts(df: pd.DataFrame, año_actual: int = 2025) -> None:
    df_tasa = calcular_tasa_publicacion(df, año_actual)
    plot_top10_bar(
        df_tasa,
        value_col="Tasa_Posts_Año",
        title="Top 10 políticos con mayor tasa de publicaciones anuales",
        yaxis_title="Posts por año"
    )

def grafico_top10_tasa_posts_partido(df: pd.DataFrame) -> None:
    top10 = (
        df[df["Tasa_Posts_Año"].notna()]
        .groupby("Partido", as_index=False)["Tasa_Posts_Año"]
        .mean()
        .round(0)
        .sort_values("Tasa_Posts_Año", ascending=False)
        .head(10)
    )

    partidos = top10["Partido"].tolist()
    tasas = top10["Tasa_Posts_Año"].tolist()
    colores = [COLOR_PARTIDOS.get(p, "#cccccc") for p in partidos]

    fig = go.Figure([
        go.Bar(
            x=partidos,
            y=tasas,
            marker_color=colores,
            text=tasas,
            textposition="outside",
            width=0.7
        )
    ])
    fig.update_layout(
        title="Top 10 partidos con mayor tasa de publicaciones anuales",
        xaxis=dict(
            title="Partido",
            categoryorder="array",
            categoryarray=partidos[::-1]
        ),
        yaxis_title="Posts por año (promedio)",
        width=900,
        height=600,
        margin=dict(l=20, r=20, t=60, b=100)
    )
    st.plotly_chart(fig)

def grafico_top10_tasa_seguidores(df: pd.DataFrame) -> None:
    df_filtrado = df[df["Tasa_Seguidores_Año"].notna()]
    plot_top10_bar(
        df_filtrado,
        value_col="Tasa_Seguidores_Año",
        title="Top 10 políticos con mayor tasa anual de ganancia de seguidores",
        yaxis_title="Seguidores por año"
    )

def grafico_top10_tasa_seguidores_partido(df: pd.DataFrame) -> None:
    top10 = (
        df[df["Tasa_Seguidores_Año"].notna()]
        .groupby("Partido", as_index=False)["Tasa_Seguidores_Año"]
        .mean()
        .round(0)
        .sort_values("Tasa_Seguidores_Año", ascending=False)
        .head(10)
    )

    partidos = top10["Partido"].tolist()
    tasas = top10["Tasa_Seguidores_Año"].tolist()
    colores = [COLOR_PARTIDOS.get(p, "#cccccc") for p in partidos]

    fig = go.Figure([
        go.Bar(
            x=partidos,
            y=tasas,
            marker_color=colores,
            text=tasas,
            textposition="outside",
            width=0.7
        )
    ])
    fig.update_layout(
        title="Top 10 partidos con mayor tasa anual de ganancia de seguidores",
        xaxis=dict(
            title="Partido",
            categoryorder="array",
            categoryarray=partidos[::-1]
        ),
        yaxis_title="Seguidores por año (promedio)",
        width=900,
        height=600,
        margin=dict(l=20, r=20, t=60, b=100)
    )
    st.plotly_chart(fig)

def mapa_variable_ccaa(
    df: pd.DataFrame,
    geojson_ccaa: dict,
    variable: str,
    aggfunc: str = "mean",
    round_decimals: int = 0,
    color_scale: str = "YlOrRd",
    title: str = "",
    label: str = ""
) -> None:
    """
    Mapa coroplético de una variable agregada por comunidad autónoma.
    """
    df_map = (
        df.groupby("Comunidad Autónoma", as_index=False)[variable]
        .agg(aggfunc)
        .round(round_decimals)
    )
    df_map = ajustar_nombres_ccaa(df_map)

    fig = px.choropleth(
        df_map,
        geojson=geojson_ccaa,
        locations="Comunidad Autónoma",
        featureidkey="properties.Texto",
        color=variable,
        color_continuous_scale=color_scale,
        title=title,
        labels={variable: label},
        width=1000,
        height=550
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(r=0, t=50, l=0, b=0))
    st.plotly_chart(fig)
