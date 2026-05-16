"""Endpoints de datasets con pandas optimizado."""
from fastapi import APIRouter, HTTPException
from pathlib import Path
import pandas as pd
import numpy as np
import csv

router = APIRouter()

BASE = Path(__file__).parent.parent.parent
PROCESADOS = BASE / "datasets_procesados"
ORIGINALES = BASE / "datasets"

INFO_DATASETS = {
    "IADIZA": {"ruta": ORIGINALES / "IADIZA" / "occurrence.txt", "delim": "\t", "encoding": "UTF-8"},
    "iNaturalist": {"ruta": ORIGINALES / "iNaturalist" / "observations.csv", "delim": ",", "encoding": "UTF-8"},
    "Xeno-canto": {"ruta": ORIGINALES / "Xeno-canto" / "Occurrence.txt", "delim": ",", "encoding": "UTF-8"},
}

def _n(v):
    if isinstance(v, (np.integer,)): return int(v)
    if isinstance(v, (np.floating,)):
        return None if np.isnan(v) else float(v)
    if isinstance(v, pd.Timestamp): return str(v)
    return v

def cargar_dataset(nombre: str) -> pd.DataFrame:
    if nombre not in INFO_DATASETS:
        raise HTTPException(404, f"Dataset '{nombre}' no encontrado")
    info = INFO_DATASETS[nombre]
    for ext in [".txt", ".csv"]:
        p = PROCESADOS / f"{nombre}{ext}"
        if p.exists():
            try:
                return pd.read_csv(p, sep=info["delim"], encoding=info["encoding"], low_memory=False)
            except Exception:
                pass
    if not info["ruta"].exists():
        raise HTTPException(404, f"Archivo no encontrado: {info['ruta']}")
    return pd.read_csv(info["ruta"], sep=info["delim"], encoding=info["encoding"], low_memory=False)

def cargar_ligero(nombre: str) -> pd.DataFrame:
    """Carga solo primeras 1000 filas para análisis rápido + metadatos."""
    if nombre not in INFO_DATASETS:
        raise HTTPException(404, f"Dataset '{nombre}' no encontrado")
    info = INFO_DATASETS[nombre]
    for ext in [".txt", ".csv"]:
        p = PROCESADOS / f"{nombre}{ext}"
        if p.exists():
            try:
                df = pd.read_csv(p, sep=info["delim"], encoding=info["encoding"], low_memory=False, nrows=1000)
                df_full = pd.read_csv(p, sep=info["delim"], encoding=info["encoding"], low_memory=False)
                return df, df_full
            except Exception:
                pass
    ruta = info["ruta"]
    df = pd.read_csv(ruta, sep=info["delim"], encoding=info["encoding"], low_memory=False, nrows=1000)
    df_full = pd.read_csv(ruta, sep=info["delim"], encoding=info["encoding"], low_memory=False)
    return df, df_full

@router.get("/datasets")
def listar():
    items = []
    for nombre, info in INFO_DATASETS.items():
        ruta = info["ruta"]
        proc = PROCESADOS / f"{nombre}.txt"
        items.append({
            "nombre": nombre,
            "archivo": ruta.name,
            "tamaño_mb": round(ruta.stat().st_size / (1024*1024), 2) if ruta.exists() else 0,
            "ultima_modificacion": ruta.stat().st_mtime if ruta.exists() else None,
            "procesado": proc.exists(),
        })
    return items

@router.get("/datasets/{nombre}")
def info(nombre: str):
    try:
        df = cargar_dataset(nombre)
    except Exception:
        raise HTTPException(500, f"No se pudo cargar {nombre}")
    nulos = df.isnull().mean().mul(100).round(2).to_dict()
    return {
        "nombre": nombre,
        "registros": int(len(df)),
        "columnas": list(df.columns),
        "nulos_porcentaje": {k: _n(v) for k, v in nulos.items()},
    }



@router.get("/datasets/{nombre}/columnas")
def columnas(nombre: str):
    """Devuelve solo las columnas sin cargar todo el dataset."""
    if nombre not in INFO_DATASETS:
        raise HTTPException(404, f"Dataset '{nombre}' no encontrado")
    info = INFO_DATASETS[nombre]
    for ext in [".txt", ".csv"]:
        p = PROCESADOS / f"{nombre}{ext}"
        if p.exists():
            try:
                df = pd.read_csv(p, sep=info["delim"], encoding=info["encoding"], nrows=1)
                return {"columnas": list(df.columns), "nombre": nombre}
            except Exception:
                pass
    ruta = info["ruta"]
    if not ruta.exists():
        raise HTTPException(404, f"Archivo no encontrado: {ruta}")
    df = pd.read_csv(ruta, sep=info["delim"], encoding=info["encoding"], nrows=1)
    return {"columnas": list(df.columns), "nombre": nombre}

@router.get("/datasets/{nombre}/mapa")
def mapa(nombre: str):
    try:
        df = cargar_dataset(nombre)
    except Exception:
        return {"total": 0, "excluidas": 0, "puntos": []}
    lat_col = "decimalLatitude" if "decimalLatitude" in df.columns else "latitudeDecimal"
    lon_col = "decimalLongitude" if "decimalLongitude" in df.columns else "longitudeDecimal"
    if lat_col not in df.columns or lon_col not in df.columns:
        return {"total": int(len(df)), "excluidas": int(len(df)), "puntos": []}
    coords = df[[lat_col, lon_col]].copy()
    coords[lat_col] = pd.to_numeric(coords[lat_col], errors="coerce")
    coords[lon_col] = pd.to_numeric(coords[lon_col], errors="coerce")
    val = coords.dropna()
    val = val[(val[lat_col] >= -90) & (val[lat_col] <= 90) & (val[lon_col] >= -180) & (val[lon_col] <= 180)]
    excl = int(len(df) - len(val))
    val = val.head(500)
    cols_extra = [c for c in ["scientificName","countryCode","stateProvince","eventDate","institutionCode","occurrenceID","datasetName"] if c in df.columns]
    extra = df.loc[val.index, cols_extra] if len(val) else pd.DataFrame()
    puntos = []
    for idx in val.index:
        p = {"decimalLatitude": _n(val.at[idx, lat_col]), "decimalLongitude": _n(val.at[idx, lon_col])}
        for c in cols_extra:
            p[c] = _n(extra.at[idx, c]) if len(extra) and idx in extra.index else None
        puntos.append(p)
    return {"total": int(len(df)), "excluidas": excl, "puntos": puntos}

@router.get("/datasets/{nombre}/valores-unicos/{columna}")
def valores_unicos(nombre: str, columna: str):
    try:
        df = cargar_dataset(nombre)
    except Exception:
        return {"valores": []}
    if columna not in df.columns:
        return {"valores": []}
    vals = df[columna].dropna().astype(str).unique().tolist()
    vals = sorted(set(v for v in vals if v.strip()))[:500]
    return {"valores": vals}

@router.get("/datasets/{nombre}/registro/{id}")
def detalle_registro(nombre: str, id: str):
    try:
        df = cargar_dataset(nombre)
    except Exception:
        raise HTTPException(500, "Error al cargar dataset")
    campo_id = next((c for c in df.columns if c.lower() in ("gbifid","id","occurrenceid","recordid")), None)
    if not campo_id:
        raise HTTPException(400, "No se detectó columna de ID")
    mask = df[campo_id].astype(str).str.strip() == id.strip()
    if not mask.any():
        raise HTTPException(404, f"ID '{id}' no encontrado")
    row = df[mask].iloc[0].to_dict()
    return {"registro": {k: _n(v) for k, v in row.items()}}



@router.get("/datasets/{nombre}/resumen-columnas")
def resumen_columnas(nombre: str):
    """Devuelve columnas y % nulos leyendo solo 1000 filas (rápido)."""
    if nombre not in INFO_DATASETS:
        raise HTTPException(404, f"Dataset '{nombre}' no encontrado")
    info = INFO_DATASETS[nombre]
    for ext in [".txt", ".csv"]:
        p = PROCESADOS / f"{nombre}{ext}"
        if p.exists():
            try:
                df = pd.read_csv(p, sep=info["delim"], encoding=info["encoding"], nrows=1000, low_memory=False)
                return _resumen(df, nombre)
            except Exception:
                pass
    ruta = info["ruta"]
    df = pd.read_csv(ruta, sep=info["delim"], encoding=info["encoding"], nrows=1000, low_memory=False)
    return _resumen(df, nombre)

def _resumen(df, nombre):
    nulos = df.isnull().mean().mul(100).round(2).to_dict()
    return {
        "nombre": nombre,
        "registros_muestra": int(len(df)),
        "columnas": list(df.columns),
        "nulos_porcentaje": {k: _n(v) for k, v in nulos.items()},
    }

@router.get("/datasets/{nombre}/docs")
def docs(nombre: str):
    docs_dir = BASE / "documentacion"
    archivos = []
    if docs_dir.exists():
        for f in sorted(docs_dir.glob("*.md")):
            try:
                with open(f, encoding="UTF-8") as fh:
                    archivos.append({"nombre": f.name, "contenido": fh.read()})
            except Exception:
                pass
    return {"documentos": archivos}
