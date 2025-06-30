import streamlit as st
import pandas as pd

class AppController:
    def __init__(self, df_metadata: pd.DataFrame):
        self.df_metadata = df_metadata

        # columnas que se excluyen por defecto del filtrado
        self.excluir = [
            'ID_Político', 'Nombre', 'Twitter', 'Legislaturas', 'Descripción',
            'Interacción_Relativa', 'Interacción', 'Posts_extraidos',
            'Tasa_Seguidores_Año', 'Tasa_Posts_Año'
        ]
        # columnas que no se grafican (numéricas puras)
        self.no_graficar = [
            'Edad', 'Posts', 'Seguidores', 'Comienzo en X/Twitter',
            'Likes', 'Retweets', 'Comentarios_Totales'
        ]

        self.columnas_filtrables = [
            col for col in df_metadata.columns if col not in self.excluir
        ]
        self.columnas_graficables = [
            col for col in self.columnas_filtrables if col not in self.no_graficar
        ]

    def aplicar_filtros(self) -> pd.DataFrame:
        df_filtrado = self.df_metadata.copy()
        st.sidebar.header("🧮 Panel de Filtros")

        for col in self.columnas_filtrables:

            # Filtros de tipo numérico
            if col in ['Edad', 'Posts', 'Seguidores', 'Likes', 'Retweets', 'Comentarios_Totales']:
                min_val, max_val = int(df_filtrado[col].min()), int(df_filtrado[col].max())
                if min_val == max_val:
                    st.sidebar.info(f"{col}: único valor disponible {min_val}")
                    rango = (min_val, max_val)
                else:
                    rango = st.sidebar.slider(col, min_val, max_val, (min_val, max_val))
                df_filtrado = df_filtrado[(df_filtrado[col] >= rango[0]) & (df_filtrado[col] <= rango[1])]

            # Filtros de tipo fecha
            elif col == "Comienzo en X/Twitter":
                min_fecha, max_fecha = df_filtrado[col].min(), df_filtrado[col].max()
                if min_fecha == max_fecha:
                    st.sidebar.info(f"Comienzo en X/Twitter: único valor {min_fecha}")
                    fechas = (min_fecha, max_fecha)
                else:
                    fechas = st.sidebar.slider(
                        "Comienzo en X/Twitter", min_fecha, max_fecha, (min_fecha, max_fecha)
                    )
                df_filtrado = df_filtrado[
                    (df_filtrado[col] >= fechas[0]) & (df_filtrado[col] <= fechas[1])
                ]

            # Filtros multiselección con texto separado por coma
            elif col == "Rango_Legislaturas":
                opciones = df_filtrado[col].dropna().str.split(", ").explode().unique()
                if len(opciones) == 1:
                    st.sidebar.info(f"Rango de Legislaturas: único valor disponible {opciones[0]}")
                    seleccionadas = [opciones[0]]
                else:
                    seleccionadas = st.sidebar.multiselect("Rango de Legislaturas", sorted(opciones))
                if seleccionadas:
                    df_filtrado = df_filtrado[
                        df_filtrado[col].fillna("").apply(
                            lambda x: any(sel in x for sel in seleccionadas)
                        )
                    ]

            # Filtros multiselección numéricos
            elif col == "Número de Legislaturas":
                opciones = sorted(df_filtrado[col].dropna().unique())
                if len(opciones) == 1:
                    st.sidebar.info(f"Número de Legislaturas: único valor disponible {opciones[0]}")
                    seleccionadas = [opciones[0]]
                else:
                    seleccionadas = st.sidebar.multiselect("Número de Legislaturas", opciones)
                if seleccionadas:
                    df_filtrado = df_filtrado[df_filtrado[col].isin(seleccionadas)]

            # Filtros multiselección generales
            else:
                opciones = df_filtrado[col].dropna().unique()
                if len(opciones) == 1:
                    st.sidebar.info(f"{col}: único valor disponible {opciones[0]}")
                    seleccionadas = [opciones[0]]
                else:
                    seleccionadas = st.sidebar.multiselect(col, sorted(opciones))
                if seleccionadas:
                    df_filtrado = df_filtrado[df_filtrado[col].isin(seleccionadas)]

        return df_filtrado


    def definir_tipo_analisis(self) -> str:
        st.sidebar.header("📊 Tipo de análisis")
        tipo_analisis = st.sidebar.radio(
            "Selecciona el tipo de análisis:",
            ["Análisis básico", "Análisis avanzado"],
            index=0
        )
        return tipo_analisis

    def definir_opciones_graficas(self, tipo_grafico: str) -> list:
        """
        Devuelve las opciones de gráficas a mostrar en el análisis básico,
        con dos modos excluyentes:
        - Mostrar todas
        - Mostrar gráficas personalizadas con Limitar/Excluir
        """
        if tipo_grafico == "Análisis avanzado":
            return []

        disponibles = self.columnas_graficables
        extras = ["Actividad temporal", "Tabla de metadata"]
        todas_opciones = extras + disponibles

        # Modo general
        modo = st.sidebar.radio(
            "¿Cómo deseas mostrar las gráficas?",
            ["Mostrar todas", "Elegir gráficas personalizadas"],
            index=0
        )

        if modo == "Mostrar todas":
            return todas_opciones

        # Modo personalizado
        seleccionadas = st.sidebar.multiselect(
            "Selecciona las gráficas personalizadas",
            todas_opciones
        )

        modo_personalizado = st.sidebar.radio(
            "Modo de selección personalizada",
            ["Limitar a", "Excluir"],
            index=0
        )

        if not seleccionadas:
            return []

        if modo_personalizado == "Limitar a":
            return seleccionadas
        else:
            return [g for g in todas_opciones if g not in seleccionadas]
