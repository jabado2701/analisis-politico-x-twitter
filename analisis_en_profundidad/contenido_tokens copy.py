import streamlit as st
from collections import Counter
import pandas as pd
import plotly.express as px
import ast
from typing import List, Tuple, Dict



@st.cache_data
def deserializar_columnas(df: pd.DataFrame, columnas: List[str]) -> pd.DataFrame:
    """
    Convierte strings de listas en listas reales para las columnas indicadas.
    """
    for col in columnas:
        if col in df.columns:
            df[col] = df[col].dropna().apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    return df


def contar_mas_frecuentes(lista_columnas: pd.Series, top_n: int = 20) -> List[Tuple[str, int]]:
    """
    Devuelve los términos más frecuentes con su frecuencia, ignorando listas vacías o nulas.
    """
    elementos = [
        item
        for sublista in lista_columnas.dropna()
        if isinstance(sublista, list) and sublista  
        for item in sublista
    ]
    return Counter(elementos).most_common(top_n)


def graficar_top(counter_list: List[Tuple[str, int]], titulo: str) -> None:
    """
    Gráfico de barras de los términos más frecuentes.
    """
    df = pd.DataFrame(counter_list, columns=["Término", "Frecuencia"])
    orden = df["Término"].tolist()
    fig = px.bar(df, x="Término", y="Frecuencia", title=titulo)
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis=dict(categoryorder="array", categoryarray=orden),
        width=1000,
        height=500,
        margin=dict(l=20, r=20, t=60, b=120)
    )
    st.plotly_chart(fig)



def analizar_tokens_entidades(df_posts: pd.DataFrame, df_comentarios: pd.DataFrame) -> None:
    """
    Muestra tokens y entidades más frecuentes en posts, comentarios y respuestas.
    """
    columnas_posts = ["Corpus_Tokens", "Entidades"]
    columnas_comentarios = [
        "Corpus_Tokens_Comentarios", "Entidades_Comentarios",
        "Corpus_Tokens_Respuestas", "Entidades_Respuestas"
    ]
    df_posts = deserializar_columnas(df_posts, columnas_posts)
    df_comentarios = deserializar_columnas(df_comentarios, columnas_comentarios)

    top_tokens = {
        "Posts": contar_mas_frecuentes(df_posts["Corpus_Tokens"]),
        "Comentarios": contar_mas_frecuentes(df_comentarios["Corpus_Tokens_Comentarios"]),
        "Respuestas": contar_mas_frecuentes(df_comentarios["Corpus_Tokens_Respuestas"])
    }
    top_entidades = {
        "Posts": contar_mas_frecuentes(df_posts["Entidades"]),
        "Comentarios": contar_mas_frecuentes(df_comentarios["Entidades_Comentarios"]),
        "Respuestas": contar_mas_frecuentes(df_comentarios["Entidades_Respuestas"])
    }

    with st.expander("🧾 Tokens y Entidades más frecuentes"):
        st.subheader("Tokens")
        for fuente, datos in top_tokens.items():
            if datos:
                graficar_top(datos, f"Tokens más frecuentes en {fuente}")
            else:
                st.info(f"No hay tokens frecuentes en {fuente}")

        st.subheader("Entidades")
        for fuente, datos in top_entidades.items():
            if datos:
                graficar_top(datos, f"Entidades más frecuentes en {fuente}")
            else:
                st.info(f"No hay entidades frecuentes en {fuente}")



def contar_por_tono(
    df: pd.DataFrame, columna_tokens: str, columna_tono: str, top_n: int = 20
) -> Dict[str, List[Tuple[str, int]]]:
    """
    Devuelve {tono: lista de tokens más frecuentes}
    """
    resultados = {}
    for tono in df[columna_tono].dropna().unique():
        subset = df[df[columna_tono] == tono]
        tokens_planos = [
            token for lista in subset[columna_tokens].dropna()
            if isinstance(lista, list) and lista  
            for token in lista
        ]
        resultados[tono] = Counter(tokens_planos).most_common(top_n)
    return resultados


def analizar_tokens_entidades_por_tono(df_posts: pd.DataFrame, df_comentarios: pd.DataFrame) -> None:
    """
    Tokens y entidades más frecuentes por tono
    """
    df_posts = deserializar_columnas(df_posts, ["Corpus_Tokens", "Entidades"])
    df_comentarios = deserializar_columnas(df_comentarios, [
        "Corpus_Tokens_Comentarios", "Entidades_Comentarios",
        "Corpus_Tokens_Respuestas", "Entidades_Respuestas"
    ])

    tokens_por_tono = {
        "Posts": contar_por_tono(df_posts, "Corpus_Tokens", "Tono"),
        "Comentarios": contar_por_tono(df_comentarios, "Corpus_Tokens_Comentarios", "Tono"),
        "Respuestas": contar_por_tono(df_comentarios, "Corpus_Tokens_Respuestas", "Tono_Respuesta")
    }
    entidades_por_tono = {
        "Posts": contar_por_tono(df_posts, "Entidades", "Tono"),
        "Comentarios": contar_por_tono(df_comentarios, "Entidades_Comentarios", "Tono"),
        "Respuestas": contar_por_tono(df_comentarios, "Entidades_Respuestas", "Tono_Respuesta")
    }

    with st.expander("🔍 Tokens y Entidades más frecuentes por tono"):
        st.subheader("Tokens por tono")
        for fuente, valores in tokens_por_tono.items():
            for tono, datos in valores.items():
                if datos:
                    graficar_top(datos, f"Tokens en {fuente} ({tono})")
                else:
                    st.info(f"No hay tokens para {fuente} ({tono})")

        st.subheader("Entidades por tono")
        for fuente, valores in entidades_por_tono.items():
            for tono, datos in valores.items():
                if datos:
                    graficar_top(datos, f"Entidades en {fuente} ({tono})")
                else:
                    st.info(f"No hay entidades para {fuente} ({tono})")



def top_elementos(df: pd.DataFrame, columna: str, n: int = 15) -> set:
    """
    Devuelve el top-n elementos de una columna con listas
    """
    counter = Counter(
        elem for lista in df[columna].dropna() if isinstance(lista, list)
        for elem in lista
    )
    return set(e for e, _ in counter.most_common(n))



def comparar_tops(
    df: pd.DataFrame,
    columna_elementos: str,
    columna_categoria: str,
    categorias: List[str],
    n: int = 15
) -> Tuple[Dict[str, set], set, Dict[str, set]]:
    """
    Compara top elementos entre categorías, devolviendo:
    - top elementos por categoría
    - comunes a todas
    - exclusivos de cada categoría
    """
    tops = {
        cat: top_elementos(df[df[columna_categoria] == cat], columna_elementos, n)
        for cat in categorias
    }
    comunes = set.intersection(*tops.values()) if len([s for s in tops.values() if s]) > 1 else set()
    exclusivos = {
        cat: tops[cat] - set.union(*(tops[c] for c in tops if c != cat))
        for cat in categorias
    }
    return tops, comunes, exclusivos


def mostrar_comparativa(titulo: str, comunes: set, exclusivos: dict, categorias: List[str]) -> None:
    """
    Presenta la comparativa de elementos comunes y exclusivos entre categorías
    """
    st.subheader(titulo)
    if comunes:
        st.markdown(f"✅ **Comunes en {', '.join(categorias)}:** {', '.join(sorted(comunes))}")
    else:
        st.info("No hay elementos comunes entre estas categorías.")

    for cat in categorias:
        excl = exclusivos.get(cat, set())
        if excl:
            st.markdown(f"🟢 **Exclusivos de {cat}:** {', '.join(sorted(excl))}")
        else:
            st.markdown(f"🟡 **Exclusivos de {cat}:** Ninguno")



def comparar_tops_streamlit(df_posts: pd.DataFrame, df_comentarios: pd.DataFrame) -> None:
    """
    Compara tokens/entidades entre Posts, Comentarios y Respuestas.
    """
    categorias = ["Posts", "Comentarios", "Respuestas"]

    df_posts = deserializar_columnas(df_posts, ["Corpus_Tokens", "Entidades"])
    df_comentarios = deserializar_columnas(df_comentarios, [
        "Corpus_Tokens_Comentarios", "Entidades_Comentarios",
        "Corpus_Tokens_Respuestas", "Entidades_Respuestas"
    ])

    df_tokens = pd.concat([
        df_posts.assign(Tipo="Posts", Tokens=df_posts["Corpus_Tokens"]),
        df_comentarios.assign(Tipo="Comentarios", Tokens=df_comentarios["Corpus_Tokens_Comentarios"]),
        df_comentarios.assign(Tipo="Respuestas", Tokens=df_comentarios["Corpus_Tokens_Respuestas"])
    ])

    tops_tokens, comunes_tokens, exclusivos_tokens = comparar_tops(df_tokens, "Tokens", "Tipo", categorias)

    df_ents = pd.concat([
        df_posts.assign(Tipo="Posts", Ents=df_posts["Entidades"]),
        df_comentarios.assign(Tipo="Comentarios", Ents=df_comentarios["Entidades_Comentarios"]),
        df_comentarios.assign(Tipo="Respuestas", Ents=df_comentarios["Entidades_Respuestas"])
    ])

    tops_ents, comunes_ents, exclusivos_ents = comparar_tops(df_ents, "Ents", "Tipo", categorias)

    with st.expander("📚 Comparativa de Tokens y Entidades entre tipos de mensaje"):
        mostrar_comparativa("🔍 Tokens", comunes_tokens, exclusivos_tokens, categorias)
        mostrar_comparativa("🔍 Entidades", comunes_ents, exclusivos_ents, categorias)


def comparar_tops_por_tono_streamlit(df_posts: pd.DataFrame) -> None:
    """
    Compara tokens/entidades entre tonos (Positivo, Negativo, Neutro).
    """
    tonos = ["Positivo", "Negativo", "Neutro"]

    df_posts = deserializar_columnas(df_posts, ["Corpus_Tokens", "Entidades"])

    df_tokens = df_posts.rename(columns={"Corpus_Tokens": "Tokens"})
    tops_tokens, comunes_tokens, exclusivos_tokens = comparar_tops(df_tokens, "Tokens", "Tono", tonos)

    df_ents = df_posts.rename(columns={"Entidades": "Ents"})
    tops_ents, comunes_ents, exclusivos_ents = comparar_tops(df_ents, "Ents", "Tono", tonos)

    with st.expander("🧠 Comparativa de Tokens y Entidades entre tonos"):
        mostrar_comparativa("🔍 Tokens", comunes_tokens, exclusivos_tokens, tonos)
        mostrar_comparativa("🔍 Entidades", comunes_ents, exclusivos_ents, tonos)


def comparar_tops_por_tema_streamlit(df_posts: pd.DataFrame) -> None:
    """
    Compara tokens/entidades entre temas.
    """
    df_posts = deserializar_columnas(df_posts, ["Corpus_Tokens", "Entidades"])

    temas = df_posts["Tema"].dropna().unique().tolist()

    df_tokens = df_posts.rename(columns={"Corpus_Tokens": "Tokens"})
    tops_tokens, comunes_tokens, exclusivos_tokens = comparar_tops(df_tokens, "Tokens", "Tema", temas)

    df_ents = df_posts.rename(columns={"Entidades": "Ents"})
    tops_ents, comunes_ents, exclusivos_ents = comparar_tops(df_ents, "Ents", "Tema", temas)

    with st.expander("📚 Comparativa de Tokens y Entidades entre temas"):
        mostrar_comparativa("🔍 Tokens", comunes_tokens, exclusivos_tokens, temas)
        mostrar_comparativa("🔍 Entidades", comunes_ents, exclusivos_ents, temas)


def obtener_top_por_tema(df: pd.DataFrame, columna_lista: str, columna_tema: str, n: int = 20) -> Dict[str, List[Tuple[str, int]]]:
    """
    Devuelve un diccionario con el top elementos de cada tema.
    """
    df = deserializar_columnas(df, [columna_lista])

    resultados = {}
    for tema in df[columna_tema].dropna().unique():
        subset = df[df[columna_tema] == tema]
        elementos = [
            item for sublista in subset[columna_lista].dropna()
            if isinstance(sublista, list) for item in sublista
        ]
        resultados[tema] = Counter(elementos).most_common(n)
    return resultados



def graficar_top_por_tema(diccionario: Dict[str, List[Tuple[str, int]]], tipo: str = "Tokens") -> None:
    """
    Grafica los elementos más frecuentes por tema.
    """
    for tema, lista in diccionario.items():
        df_tema = pd.DataFrame(lista, columns=["Término", "Frecuencia"])
        orden = df_tema["Término"].tolist()
        fig = px.bar(
            df_tema,
            x="Término",
            y="Frecuencia",
            title=f"{tipo} más frecuentes en el tema: {tema}",
        )
        fig.update_layout(
            xaxis=dict(categoryorder="array", categoryarray=orden),
            xaxis_tickangle=-45,
            width=1000,
            height=500,
            margin=dict(l=20, r=20, t=60, b=120)
        )
        st.plotly_chart(fig)


def analizar_tokens_entidades_por_tema(df_posts: pd.DataFrame) -> None:
    """
    Muestra tokens y entidades más frecuentes por tema.
    """
    df_posts = deserializar_columnas(df_posts, ["Corpus_Tokens", "Entidades"])

    top_tokens = obtener_top_por_tema(df_posts, "Corpus_Tokens", "Tema")
    top_entidades = obtener_top_por_tema(df_posts, "Entidades", "Tema")

    with st.expander("📚 Tokens y Entidades más frecuentes por tema"):
        st.subheader("Tokens por tema")
        graficar_top_por_tema(top_tokens, tipo="Tokens")

        st.subheader("Entidades por tema")
        graficar_top_por_tema(top_entidades, tipo="Entidades")
