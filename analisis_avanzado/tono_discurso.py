import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import COLOR_PARTIDOS
from analisis_avanzado.utils import ajustar_nombres_ccaa


def calcular_proporcion_tono(
    df_posts: pd.DataFrame,
    df_metadata: pd.DataFrame
) -> pd.DataFrame:
    """
    Calcula la proporción de posts de cada tono (Positivo, Negativo, Neutro)
    para cada político, y añade sus datos de nombre y partido.
    """
    tono_posts_politico = (
        df_posts.groupby(["ID_Político", "Tono"])
        .size()
        .reset_index(name="Cantidad")
    )
    tono_posts_politico["Proporción"] = tono_posts_politico.groupby("ID_Político")["Cantidad"].transform(
        lambda x: x / x.sum()
    )

    return tono_posts_politico.merge(
        df_metadata[["ID_Político", "Nombre", "Partido"]],
        on="ID_Político",
        how="left"
    )


def graficos_proporcion_tono_partido(
    df_posts: pd.DataFrame,
    df_metadata: pd.DataFrame
) -> None:
    """
    Muestra top 10 partidos por proporción de posts según tono.
    """
    proporciones = calcular_proporcion_tono(df_posts, df_metadata)

    proporcion_partido = (
        proporciones.groupby(["Partido", "Tono"], as_index=False)["Proporción"]
        .mean()
    )

    for tono in ["Positivo", "Negativo", "Neutro"]:
        df_tono = (
            proporcion_partido[proporcion_partido["Tono"] == tono]
            .sort_values("Proporción", ascending=False)
            .head(10)
        )

        orden = df_tono["Partido"].iloc[::-1]
        colores = [COLOR_PARTIDOS.get(p, "#cccccc") for p in df_tono["Partido"]]

        fig = go.Figure([
            go.Bar(
                x=df_tono["Partido"],
                y=df_tono["Proporción"],
                marker_color=colores,
                text=df_tono["Proporción"].apply(lambda x: f"{x:.1%}"),
                textposition="outside",
                width=0.7
            )
        ])
        fig.update_layout(
            title=f"Top 10 partidos con mayor proporción de posts {tono.lower()}",
            xaxis=dict(categoryorder="array", categoryarray=orden),
            yaxis_title="Proporción",
            width=1000,
            height=550
        )
        st.plotly_chart(fig)


def graficos_proporcion_tono_politico(
    df_posts: pd.DataFrame,
    df_metadata: pd.DataFrame
) -> None:
    """
    Muestra top 10 políticos con mayor proporción de posts según tono.
    """
    proporciones = calcular_proporcion_tono(df_posts, df_metadata)

    for tono in ["Positivo", "Negativo", "Neutro"]:
        df_tono = (
            proporciones[proporciones["Tono"] == tono]
            .sort_values("Proporción", ascending=False)
            .head(10)
        )
        orden = df_tono["Nombre"].iloc[::-1]

        fig = go.Figure()
        for partido in df_tono["Partido"].unique():
            datos_partido = df_tono[df_tono["Partido"] == partido]
            fig.add_trace(go.Bar(
                x=datos_partido["Nombre"],
                y=datos_partido["Proporción"],
                name=partido,
                marker_color=COLOR_PARTIDOS.get(partido, "#cccccc"),
                text=datos_partido["Proporción"].apply(lambda x: f"{x:.1%}"),
                textposition="outside",
                width=0.7
            ))

        fig.update_layout(
            title=f"Top 10 políticos con mayor proporción de posts {tono.lower()}",
            xaxis=dict(categoryorder="array", categoryarray=orden),
            yaxis_title="Proporción",
            legend_title="Partido",
            width=1000,
            height=600
        )
        st.plotly_chart(fig)


def graficos_mapa_tono_ccaa(
    df_posts: pd.DataFrame,
    df_metadata: pd.DataFrame,
    geojson_ccaa: dict
) -> None:
    """
    Muestra mapas coropléticos con proporción de tonos (Positivo, Negativo, Neutro)
    por comunidad autónoma.
    """
    posts_con_ccaa = df_posts.merge(
        df_metadata[["ID_Político", "Comunidad Autónoma"]],
        on="ID_Político",
        how="left"
    )

    tono_ccaa = (
        posts_con_ccaa.groupby(["Comunidad Autónoma", "Tono"])
        .size()
        .reset_index(name="Cantidad")
    )
    tono_ccaa["Total"] = tono_ccaa.groupby("Comunidad Autónoma")["Cantidad"].transform("sum")
    tono_ccaa["Proporción"] = tono_ccaa["Cantidad"] / tono_ccaa["Total"]

    tono_ccaa = ajustar_nombres_ccaa(tono_ccaa)

    for tono, escala in zip(["Positivo", "Negativo", "Neutro"], ["Greens", "Reds", "Blues"]):
        df_tono = tono_ccaa[tono_ccaa["Tono"] == tono]
        fig = px.choropleth(
            df_tono,
            geojson=geojson_ccaa,
            locations="Comunidad Autónoma",
            featureidkey="properties.Texto",
            color="Proporción",
            color_continuous_scale=escala,
            title=f"Proporción de tono {tono.lower()} por Comunidad Autónoma",
            labels={"Proporción": "Proporción"},
            width=900,
            height=500
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin=dict(r=0, t=50, l=0, b=0))
        st.plotly_chart(fig)


def graficar_tono_por_tema_individual(
    df_posts: pd.DataFrame,
    df_metadata_filtrado: pd.DataFrame
) -> None:
    """
    Gráfico de barras por tema con proporciones de tono (Negativo, Neutro, Positivo),
    filtrando solo posts de políticos que cumplen los filtros activos.
    """
    ids_filtrados = df_metadata_filtrado["ID_Político"].unique()
    df_filtrado_posts = df_posts[df_posts["ID_Político"].isin(ids_filtrados)].copy()

    proporcion = (
        df_filtrado_posts.groupby(["Tema", "Tono"])
        .size()
        .reset_index(name="Cantidad")
    )
    proporcion["Proporción"] = proporcion.groupby("Tema")["Cantidad"].transform(lambda x: x / x.sum())

    temas = proporcion["Tema"].dropna().unique()
    orden_tonos = ["Negativo", "Neutro", "Positivo"]
    color_map = {"Positivo": "green", "Negativo": "red", "Neutro": "gray"}

    for tema in temas:
        df_tema = proporcion[proporcion["Tema"] == tema]
        if df_tema.empty:
            continue

        colores = [color_map.get(tono, "gray") for tono in df_tema["Tono"]]

        fig = go.Figure([
            go.Bar(
                x=df_tema["Tono"],
                y=df_tema["Proporción"],
                text=df_tema["Proporción"].map("{:.1%}".format),
                textposition="outside",
                marker_color=colores,
                width=0.7
            )
        ])
        fig.update_layout(
            title=f"Distribución de tono en el tema: {tema}",
            xaxis=dict(
                title="Tono",
                categoryorder="array",
                categoryarray=orden_tonos
            ),
            yaxis_title="Proporción",
            width=900,
            height=500,
            margin=dict(l=20, r=20, t=50, b=100)
        )
        st.plotly_chart(fig)
