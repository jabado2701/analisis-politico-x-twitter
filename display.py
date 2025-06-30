import streamlit as st
import visualizaciones_basicas as vb
import analisis_avanzado.popularidad_actividad as pop
import analisis_avanzado.interaccion_impacto as inter
import analisis_avanzado.tono_discurso as tono
import analisis_avanzado.contenido_tokens as cont
import pandas as pd


def mostrar_basico(
    df_filtrado: pd.DataFrame,
    tipo_grafico: str,
    opciones_graficas: list,
    df_posts: pd.DataFrame,
    df_comentarios: pd.DataFrame
):
    """
    Análisis básico:
    - Gráficos de distribución (tarta)
    - Serie temporal de actividad
    - Tabla de metadata
    """
    vb.mostrar_graficos_basicos(df_filtrado, tipo_grafico, opciones_graficas)

    if "Actividad temporal" in opciones_graficas:
        vb.mostrar_actividad_temporal(df_posts, df_comentarios)

    if "Tabla de metadata" in opciones_graficas:
        vb.mostrar_tabla_metadata(df_filtrado)


def mostrar_analisis_avanzado(
    df_filtrado: pd.DataFrame,
    df_posts: pd.DataFrame,
    df_comentarios: pd.DataFrame,
    geojson_ccaa: dict
):
    """
    Análisis avanzado completo:
    organizado en 4 bloques temáticos y subapartados con expanders
    """

    # 1️⃣ Popularidad y Actividad
    with st.expander("👤 Popularidad y Actividad"):
        with st.expander("📈 Popularidad"):
            pop.grafico_top10_politicos_seguidores(df_filtrado)
            pop.grafico_top10_partidos_seguidores(df_filtrado)
            pop.grafico_top10_tasa_seguidores(df_filtrado)
            pop.grafico_top10_tasa_seguidores_partido(df_filtrado)
            pop.mapa_variable_ccaa(
                df_filtrado, geojson_ccaa,
                variable="Seguidores",
                aggfunc="mean",
                round_decimals=0,
                color_scale="YlOrRd",
                title="Popularidad media por Comunidad Autónoma",
                label="Seguidores promedio"
            )
        with st.expander("📝 Actividad"):
            pop.grafico_top10_politicos_posts(df_filtrado)
            pop.grafico_top10_partidos_posts(df_filtrado)
            pop.grafico_top10_tasa_posts(df_filtrado)
            pop.grafico_top10_tasa_posts_partido(df_filtrado)
            pop.mapa_variable_ccaa(
                df_filtrado, geojson_ccaa,
                variable="Posts",
                aggfunc="mean",
                round_decimals=0,
                color_scale="Greens",
                title="Frecuencia media de publicación por Comunidad Autónoma",
                label="Nº medio de publicaciones"
            )

    # 2️⃣ Interacción e Impacto
    with st.expander("🔁 Interacción e Impacto"):
        with st.expander("💬 Interacción absoluta"):
            inter.grafico_top10_interaccion(df_filtrado)
            inter.grafico_top10_interaccion_partido(df_filtrado)
        with st.expander("📊 Interacción relativa"):
            inter.grafico_top10_interaccion_relativa_politicos(df_filtrado)
            inter.grafico_top10_interaccion_relativa_partidos(df_filtrado)
            pop.mapa_variable_ccaa(
                df_filtrado, geojson_ccaa,
                variable="Interacción_Relativa",
                aggfunc="mean",
                round_decimals=3,
                color_scale="Blues",
                title="Interacción relativa media por Comunidad Autónoma",
                label="Interacción / Seguidor"
            )

    # 3️⃣ Tono del Discurso
    with st.expander("🗣️ Tono del Discurso"):
        with st.expander("📊 Proporción de tono"):
            tono.graficos_proporcion_tono_partido(df_posts, df_filtrado)
            tono.graficos_proporcion_tono_politico(df_posts, df_filtrado)
        with st.expander("🗺️ Tono por territorio"):
            tono.graficos_mapa_tono_ccaa(df_posts, df_filtrado, geojson_ccaa)
        with st.expander("📚 Tono por tema"):
            tono.graficar_tono_por_tema_individual(df_posts, df_filtrado)

    # 4️⃣ Contenido
    with st.expander("🧾 Contenido: Palabras clave y Entidades"):
        with st.expander("🔠 Frecuencias"):
            cont.analizar_tokens_entidades(df_posts, df_comentarios, df_filtrado)
            cont.analizar_tokens_entidades_por_tono(df_posts, df_comentarios, df_filtrado)
        with st.expander("📚 Comparativas"):
            cont.comparar_tops_streamlit(df_posts, df_comentarios, df_filtrado)
            cont.comparar_tops_por_tono_streamlit(df_posts, df_filtrado)
            cont.analizar_tokens_entidades_por_tema(df_posts, df_filtrado)
            cont.comparar_tops_por_tema_streamlit(df_posts, df_filtrado)
