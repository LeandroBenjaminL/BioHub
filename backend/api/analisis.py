"""Endpoints de análisis y gráficos."""
from fastapi import APIRouter
from api.datasets import cargar_dataset, INFO_DATASETS, BASE
from pathlib import Path
import pandas as pd
import numpy as np

router = APIRouter()

def _try_date(col):
    try:
        return pd.to_datetime(col, errors="coerce", utc=True)
    except Exception:
        try:
            return pd.to_datetime(col, errors="coerce")
        except Exception:
            return pd.Series([pd.NaT] * len(col))

def _n(v):
    if isinstance(v, (np.integer,)): return int(v)
    if isinstance(v, (np.floating,)):
        return None if np.isnan(v) else float(v)
    return v

def _contar_lineas(ruta, delim=","):
    """Estima cantidad de líneas por tamaño de archivo (rápido)."""
    try:
        # Lee solo las primeras líneas y estima por tamaño
        with open(ruta, encoding="UTF-8") as f:
            primero = f.readline()
            segundo = f.readline()
            if not segundo:
                return 0
            tam_est = ruta.stat().st_size
            # Tamaño promedio por línea
            tam_prom = (len(primero) + len(segundo)) / 2
            estimado = int(tam_est / max(tam_prom, 1))
            return max(estimado - 1, 0)
    except Exception:
        return 0

def _stats_liviano(ruta, nombre, delim, enc="UTF-8"):
    """Obtiene stats de un dataset sin cargarlo entero."""
    try:
        total = _contar_lineas(ruta, delim)
        df = pd.read_csv(ruta, sep=delim, encoding=enc, low_memory=False, nrows=2000)
        completitud = round(float(df.notna().mean().mean() * 100), 2)
        coord = 0
        for lc in ["decimalLatitude", "latitudeDecimal"]:
            for lnc in ["decimalLongitude", "longitudeDecimal"]:
                if lc in df.columns and lnc in df.columns:
                    c = df[[lc, lnc]].dropna()
                    coord = len(c)
                    break
            if coord: break
        coord_pct = round(coord / len(df) * 100, 2) if len(df) else 0.0
        fecha_pct = 0.0
        if "eventDate" in df.columns:
            f = _try_date(df["eventDate"])
            fecha_pct = round(float(f.notna().mean() * 100), 2)
        return {"nombre": nombre, "registros": total, "coordenadas_validas_pct": coord_pct,
                "fecha_valida_pct": fecha_pct, "campos_completados_pct": completitud}
    except Exception as e:
        return {"nombre": nombre, "error": str(e)}

@router.get("/datasets/{nombre}/graficos/por-pais")
def por_pais(nombre: str, top_n: int = 10):
    try:
        df = cargar_dataset(nombre)
    except Exception:
        return {"etiquetas": [], "valores": [], "error": "No se pudo cargar"}
    col = "countryCode" if "countryCode" in df.columns else "country"
    col = col if col in df.columns else (list(df.columns)[0] if len(df.columns) else "")
    if col not in df.columns:
        return {"etiquetas": [], "valores": []}
    counts = df[col].value_counts().head(top_n)
    return {"etiquetas": [_n(k) for k in counts.index], "valores": [_n(v) for v in counts.values]}

@router.get("/datasets/{nombre}/graficos/por-ano")
def por_ano(nombre: str):
    try:
        df = cargar_dataset(nombre)
    except Exception:
        return {"etiquetas": [], "valores": [], "excluidas": 0}
    if "eventDate" not in df.columns:
        return {"etiquetas": [], "valores": [], "excluidas": 0}
    fechas = _try_date(df["eventDate"])
    excluidas = int(fechas.isna().sum())
    anos = fechas.dt.year.dropna().value_counts().sort_index()
    return {"etiquetas": [int(a) for a in anos.index], "valores": [int(v) for v in anos.values], "excluidas": excluidas}

@router.get("/datasets/{nombre}/graficos/taxonomia")
def taxonomia(nombre: str, nivel: str = "class"):
    try:
        df = cargar_dataset(nombre)
    except Exception:
        return {"etiquetas": [], "valores": []}
    if nivel not in df.columns:
        niveles = [c for c in ["class", "order", "family"] if c in df.columns]
        if not niveles:
            return {"etiquetas": [], "valores": []}
        nivel = niveles[0]
    counts = df[nivel].value_counts().head(15)
    return {"etiquetas": [_n(k) for k in counts.index], "valores": [_n(v) for v in counts.values]}

@router.get("/datasets/{nombre}/graficos/completitud")
def completitud(nombre: str):
    try:
        df = cargar_dataset(nombre)
    except Exception:
        return {"columnas": [], "porcentajes": []}
    pct = df.notna().mean().mul(100).sort_values(ascending=False).round(2)
    return {"columnas": [_n(k) for k in pct.index], "porcentajes": [_n(v) for v in pct.values]}

@router.get("/datasets/comparativa")
def comparativa():
    items = []
    for nombre, info in INFO_DATASETS.items():
        items.append(_stats_liviano(info["ruta"], nombre, info["delim"], info["encoding"]))
    return items

@router.get("/datasets/{nombre}/resumen")
def resumen(nombre: str, columna: str = "", texto: str = ""):
    try:
        df = cargar_dataset(nombre)
    except Exception:
        return {"especies_unicas": 0, "paises": 0, "provincias": 0, "observadores": 0}
    if columna in df.columns and texto:
        df = df[df[columna].astype(str).str.contains(texto, case=False, na=False)]
    return {
        "especies_unicas": int(df["scientificName"].nunique()) if "scientificName" in df else 0,
        "paises": int(df["countryCode"].nunique()) if "countryCode" in df else 0,
        "provincias": int(df["stateProvince"].nunique()) if "stateProvince" in df else 0,
        "observadores": int(df["recordedBy"].nunique()) if "recordedBy" in df else 0,
    }
