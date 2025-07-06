import streamlit as st
import pandas as pd
from data_loader import cargar_datos, cargar_mapa_geojson
import controllers as ctrl
import display as dp

st.set_page_config(
    layout="wide",
    page_title="Análisis Político Twitter",
    page_icon="📊"
)

df_metadata, df_posts, df_comentarios = cargar_datos()
geojson_ccaa = cargar_mapa_geojson()

if df_metadata.empty or df_posts.empty or df_comentarios.empty:
    st.error("❌ Error al cargar alguno de los datasets. Por favor revisa el archivo.")
    st.stop()

controller = ctrl.AppController(df_metadata)

tipo_analisis = controller.definir_tipo_analisis()

df_filtrado = controller.aplicar_filtros()

opciones_graficas = controller.definir_opciones_graficas(tipo_analisis)

if tipo_analisis == "Análisis en profundidad":
    st.title("📊 Análisis en profundidad de la Actividad Política en X/Twitter")
else:
    st.title("📊 Análisis Básico de Políticos en X/Twitter")
    st.markdown(
        "Explorador visual e interactivo del comportamiento político en redes sociales."
    )

if tipo_analisis == "Análisis en profundidad":
    dp.mostrar_analisis_en_profundidad(df_filtrado, df_posts, df_comentarios, geojson_ccaa)
else:
    dp.mostrar_basico(df_filtrado, tipo_analisis, opciones_graficas, df_posts, df_comentarios)
