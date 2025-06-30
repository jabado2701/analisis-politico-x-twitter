import pandas as pd
import geopandas as gpd
from shapely import affinity
import streamlit as st
from typing import Tuple

@st.cache_data
def cargar_datos() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Carga los datos de Excel con un spinner clásico
    """
    try:
        with st.spinner("Cargando datos..."):
            ruta = "datasets/politicos_etiquetado_final.xlsx"
            df_metadata = pd.read_excel(ruta, sheet_name="Metadata")
            df_posts = pd.read_excel(ruta, sheet_name="Posts")
            df_comentarios = pd.read_excel(ruta, sheet_name="Comentarios")
        return df_metadata, df_posts, df_comentarios
    except FileNotFoundError:
        st.error(f"No se encontró el archivo de datos en {ruta}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


@st.cache_data
def cargar_mapa_geojson() -> dict:
    """
    Carga y transforma el shapefile a geojson
    """
    try:
        ruta_shp = "mapas/ComunidadesAutonomas_ETRS89_30N/Comunidades_Autonomas_ETRS89_30N.shp"
        gdf = gpd.read_file(ruta_shp)
    except Exception as e:
        st.error(f"No se pudo leer el shapefile: {e}")
        return {}

    try:
        idx_canarias = gdf[gdf["Texto"] == "Canarias"].index[0]
        gdf.loc[idx_canarias, "geometry"] = affinity.translate(
            gdf.loc[idx_canarias, "geometry"], xoff=550_000, yoff=750_000
        )
        gdf = gdf.to_crs(epsg=4326)
        return gdf.__geo_interface__
    except Exception as e:
        st.error(f"Error al transformar el mapa: {e}")
        return {}
