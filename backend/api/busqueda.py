"""Búsqueda con filtros combinables."""
from fastapi import APIRouter, Query, HTTPException
from api.datasets import cargar_dataset, _n
import pandas as pd

router = APIRouter()

def _col(df, posibles):
    for c in posibles:
        if c in df.columns:
            return c
    return None

@router.post("/datasets/{nombre}/buscar")
def buscar(
    nombre: str,
    columna: str = Query(""),
    texto: str = Query(""),
    cientifico: list[str] = Query(default=[]),
    pais: list[str] = Query(default=[]),
    provincia: list[str] = Query(default=[]),
    observador: str = Query(default=""),
    fecha_desde: str = Query(default=""),
    fecha_hasta: str = Query(default=""),
):
    df = cargar_dataset(nombre)

    if columna and columna in df.columns and texto:
        df = df[df[columna].astype(str).str.contains(texto, case=False, na=False)]

    if cientifico:
        c = _col(df, ["scientificName"])
        if c:
            df = df[df[c].astype(str).str.lower().isin([s.lower() for s in cientifico])]

    if pais:
        c = _col(df, ["countryCode", "country"])
        if c:
            df = df[df[c].astype(str).str.lower().isin([p.lower() for p in pais])]

    if provincia:
        c = _col(df, ["stateProvince"])
        if c:
            df = df[df[c].astype(str).str.lower().isin([p.lower() for p in provincia])]

    if observador:
        c = _col(df, ["recordedBy", "observer"])
        if c:
            df = df[df[c].astype(str).str.contains(observador, case=False, na=False)]

    if fecha_desde or fecha_hasta:
        c = _col(df, ["eventDate"])
        if c:
            try:
                fechas = pd.to_datetime(df[c], errors="coerce", utc=True)
                if fecha_desde:
                    df = df[fechas >= pd.Timestamp(fecha_desde)]
                if fecha_hasta:
                    df = df[fechas <= pd.Timestamp(fecha_hasta)]
            except Exception:
                pass

    RELEVANTES = ["gbifID","occurrenceID","scientificName","countryCode","stateProvince",
                  "eventDate","decimalLatitude","decimalLongitude","institutionCode",
                  "recordedBy","kingdom","phylum","class","order","family","genus","datasetName"]
    relevantes = [c for c in RELEVANTES if c in df.columns]
    if not relevantes:
        relevantes = list(df.columns)[:8]

    total = int(len(df))
    resultados = df.head(200).to_dict(orient="records")
    for r in resultados:
        for k, v in r.items():
            r[k] = _n(v)

    return {"total": total, "mostrando": min(200, total), "columnas_relevantes": relevantes, "resultados": resultados}
