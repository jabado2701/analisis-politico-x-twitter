
```markdown
# 📊 Análisis Político en X/Twitter

Esta aplicación en Streamlit permite analizar la actividad de políticos españoles en la red social X/Twitter, utilizando datos de carácter público (extraídos de fuentes oficiales como el Congreso de los Diputados o Wikipedia). Incluye análisis básico y avanzado con diferentes visualizaciones interactivas.

## 🚀 Funcionalidades

✅ Distribución de actividad por partido y político  
✅ Evolución temporal de publicaciones  
✅ Popularidad y tasas de seguidores  
✅ Mapas coropléticos por Comunidad Autónoma  
✅ Análisis de tono del discurso  
✅ Tokens y entidades más frecuentes en mensajes  

## 📁 Estructura del proyecto


analisis-politico-x-twitter/
├── analisis\_avanzado/
├── datasets/
│   └── politicos\_etiquetado\_final.xlsx
├── mapas/
│   ├── ComunidadesAutonomas\_ETRS89\_30N/
│   ├── Municipios\_IGN/
│   └── Provincias\_ETRS89\_30N/
├── app.py
├── config.py
├── controllers.py
├── data\_loader.py
├── display.py
├── requirements.txt
└── README.md

## ⚙️ Requisitos

- Python 3.9+  
- Streamlit  
- pandas  
- geopandas  
- shapely  
- plotly
````

## 🖥️ Ejecución local

1️⃣ Clonar el repositorio:  

```bash
git clone https://github.com/jabado2701/analisis-politico-x-twitter.git
cd analisis-politico-x-twitter
````

2️⃣ Instalar dependencias:

```bash
pip install -r requirements.txt
```

3️⃣ Ejecutar la aplicación:

```bash
streamlit run app.py
```

## ☁️ Despliegue en Streamlit Cloud

La app está preparada para ser desplegada directamente en [Streamlit Cloud](https://streamlit.io/cloud).

* Selecciona como archivo principal `app.py`
* Indica la rama `main`

**Importante**: los datos públicos ya están incluidos en el repositorio para facilitar la puesta en producción.

## 📄 Fuentes de datos

* Congreso de los Diputados de España
* Wikipedia
* Datos abiertos oficiales de entidades públicas

## ⚠️ Aviso de privacidad

Esta aplicación **no** gestiona datos privados ni sensibles. Todos los datos provienen de fuentes públicas.
