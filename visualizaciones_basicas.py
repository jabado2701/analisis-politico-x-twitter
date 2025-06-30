import streamlit as st
import plotly.express as px
import pandas as pd
from config import COLOR_PARTIDOS, generar_paleta

__all__ = [
    "mostrar_graficos_basicos",
    "mostrar_actividad_temporal",
    "mostrar_tabla_metadata",
]


def mostrar_graficos_basicos(df: pd.DataFrame, tipo: str, columnas: list):
    """
    Visualización de gráficos básicos tipo tarta.
    """
    for col in columnas:
        if col in ["Actividad temporal", "Tabla de metadata"]:
            continue

        st.markdown("---")
        st.subheader(f"📊 Distribución por {col}")

        if tipo == "Análisis básico":
            fig = px.pie(
                df,
                names=col,
                title=f"Distribución por {col}",
                color=col if col == "Partido" else None,
                color_discrete_map=COLOR_PARTIDOS if col == "Partido" else generar_paleta(df[col].unique())
            )
            fig.update_traces(hovertemplate="%{label}=%{value}")

            fig.update_layout(width=1200, height=600)
            st.plotly_chart(fig)


@st.cache_data
def preparar_actividad_temporal(df_posts: pd.DataFrame, df_comentarios: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara el dataframe de actividad temporal para ser graficado,
    utilizando cache para no recalcularlo en cada recarga.
    """
    posts_fecha = (
        pd.to_datetime(df_posts["Fecha_Publicación"], errors='coerce')
        .dt.date.value_counts()
        .sort_index()
    )
    comentarios_fecha = (
        pd.to_datetime(df_comentarios["Fecha_Publicación"], errors='coerce')
        .dt.date.value_counts()
        .sort_index()
    )
    df_plot = pd.DataFrame({
        "Fecha": list(posts_fecha.index) + list(comentarios_fecha.index),
        "Cantidad": list(posts_fecha.values) + list(comentarios_fecha.values),
        "Tipo": ["Posts"] * len(posts_fecha) + ["Comentarios"] * len(comentarios_fecha)
    })
    return df_plot


def mostrar_actividad_temporal(df_posts: pd.DataFrame, df_comentarios: pd.DataFrame):
    """
    Visualiza la evolución temporal de posts y comentarios.
    """
    st.markdown("---")
    st.subheader("📆 Actividad por Fecha (Posts y Comentarios)")

    try:
        df_plot = preparar_actividad_temporal(df_posts, df_comentarios)
        fig = px.line(df_plot, x="Fecha", y="Cantidad", color="Tipo", title="Evolución temporal de actividad")
        fig.update_layout(width=1200, height=500)
        st.plotly_chart(fig)
    except Exception as e:
        st.warning(f"No se pudo generar la serie temporal: {e}")


def mostrar_tabla_metadata(df: pd.DataFrame):
    """
    Muestra la tabla completa de metadata filtrada.
    """
    st.markdown("---")
    st.subheader("📋 Tabla filtrada de Metadata")
    st.dataframe(df)
