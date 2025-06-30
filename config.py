import plotly.express as px
import itertools
from typing import List, Dict

# Mapa fijo de colores por partido
COLOR_PARTIDOS: Dict[str, str] = {
    "PSOE": "#ff0000", "PP": "#189ad3", "SUMAR": "#ff0065", "VOX": "#74d600",
    "JxCAT-JUNTS": "#43e8d8", "EAJ-PNV": "#389844", "ERC": "#fdb73e",
    "EH Bildu": "#3fa0a3", "CCa": "#fffff2", "PRC": "#d6ff00", "BNG": "#b0cfff",
    "Más Madrid": "#52eb86", "UPN": "#0059b3",
}

def generar_paleta(categorias: List[str]) -> Dict[str, str]:
    """
    Genera un mapa de colores ciclando colores base para categorías arbitrarias.
    """
    base = px.colors.qualitative.Set2 + px.colors.qualitative.Pastel
    return dict(zip(categorias, itertools.cycle(base)))

