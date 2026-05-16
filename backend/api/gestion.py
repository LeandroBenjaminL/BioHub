"""CRUD de registros."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.datasets import cargar_dataset, _n, PROCESADOS, INFO_DATASETS
import pandas as pd
from pathlib import Path
from datetime import datetime

router = APIRouter()
LOG = Path(__file__).parent.parent.parent / "logs" / "operations.log"

def _log(ds, op, cant, error=False):
    LOG.parent.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    estado = "ERROR" if error else "OK"
    with open(LOG, "a", encoding="UTF-8") as f:
        f.write(f"{ts} | {ds} | {op} | {cant} | {estado}\n")

def _guardar(nombre, df):
    info = INFO_DATASETS.get(nombre)
    salida = PROCESADOS / f"{nombre}.txt"
    df.to_csv(salida, sep=info["delim"] if info else ",", index=False, encoding="UTF-8")

class InsertarReq(BaseModel):
    datos: dict

class ActualizarReq(BaseModel):
    id: str
    cambios: dict

class EliminarPreviewReq(BaseModel):
    columna: str = ""
    valores: list[str] = []
    condicion: str = ""
    valor: str = ""

class EliminarReq(BaseModel):
    columna: str = ""
    valores: list[str] = []
    condicion: str = ""
    valor: str = ""
    confirmado: bool = False

@router.post("/datasets/{nombre}/insertar")
def insertar(nombre: str, req: InsertarReq):
    df = cargar_dataset(nombre)
    errores = []
    if "decimalLatitude" in req.datos:
        try:
            lat = float(req.datos["decimalLatitude"])
            if not -90 <= lat <= 90:
                errores.append("decimalLatitude fuera de rango [-90, 90]")
        except ValueError:
            errores.append("decimalLatitude debe ser numérico")
    if "decimalLongitude" in req.datos:
        try:
            lon = float(req.datos["decimalLongitude"])
            if not -180 <= lon <= 180:
                errores.append("decimalLongitude fuera de rango [-180, 180]")
        except ValueError:
            errores.append("decimalLongitude debe ser numérico")
    if errores:
        _log(nombre, "INSERT", 0, True)
        raise HTTPException(400, {"errores": errores})

    nuevo = pd.DataFrame([req.datos])
    df = pd.concat([df, nuevo], ignore_index=True)
    _guardar(nombre, df)
    _log(nombre, "INSERT", 1)
    return {"mensaje": "Registro insertado", "total": int(len(df))}

@router.put("/datasets/{nombre}/actualizar")
def actualizar(nombre: str, req: ActualizarReq):
    df = cargar_dataset(nombre)
    campo_id = _col(df, ["gbifID","id","occurrenceID","recordID","identifier"])
    if not campo_id:
        raise HTTPException(400, "No se detectó columna de ID")
    mask = df[campo_id].astype(str).str.strip() == req.id.strip()
    if not mask.any():
        raise HTTPException(404, f"ID '{req.id}' no encontrado")
    idx = mask.idxmax()
    resumen = []
    for col, val in req.cambios.items():
        if col in df.columns:
            viejo = str(df.at[idx, col]) if pd.notna(df.at[idx, col]) else ""
            nuevo = str(val)
            if viejo != nuevo:
                df.at[idx, col] = val
                resumen.append({"campo": col, "anterior": viejo, "nuevo": nuevo})
    if not resumen:
        return {"mensaje": "Sin cambios", "modificados": 0, "resumen": []}
    _guardar(nombre, df)
    _log(nombre, "UPDATE", 1)
    return {"mensaje": "Registro actualizado", "modificados": len(resumen), "resumen": resumen}

@router.post("/datasets/{nombre}/eliminar/preview")
def preview_eliminar(nombre: str, req: EliminarPreviewReq):
    df = cargar_dataset(nombre)
    if req.columna not in df.columns:
        raise HTTPException(400, f"Columna '{req.columna}' no existe")
    antes = len(df)
    if req.valores:
        mask = df[req.columna].astype(str).str.lower().isin([v.lower() for v in req.valores])
    elif req.condicion:
        ops = {"==": "eq", "!=": "ne", ">": "gt", ">=": "ge", "<": "lt", "<=": "le"}
        op = ops.get(req.condicion)
        if not op:
            raise HTTPException(400, f"Operador '{req.condicion}' inválido")
        try:
            mask = getattr(df[req.columna].astype(str), op)(req.valor)
        except Exception as e:
            raise HTTPException(400, f"Error: {e}")
    else:
        raise HTTPException(400, "Especificá valores o condición")
    preview = df[mask].head(10).to_dict(orient="records")
    for r in preview:
        for k, v in r.items():
            r[k] = _n(v)
    return {
        "total_afectados": int(mask.sum()), "total_dataset": antes,
        "porcentaje": round(int(mask.sum()) / antes * 100, 2) if antes else 0,
        "preview": preview,
    }

@router.post("/datasets/{nombre}/eliminar")
def eliminar(nombre: str, req: EliminarReq):
    if not req.confirmado:
        raise HTTPException(400, "Debés confirmar la eliminación")
    df = cargar_dataset(nombre)
    antes = len(df)
    if req.columna not in df.columns:
        raise HTTPException(400, f"Columna '{req.columna}' no existe")
    if req.valores:
        mask = df[req.columna].astype(str).str.lower().isin([v.lower() for v in req.valores])
    elif req.condicion:
        ops = {"==": "eq", "!=": "ne", ">": "gt", ">=": "ge", "<": "lt", "<=": "le"}
        op = ops.get(req.condicion)
        if not op:
            raise HTTPException(400, f"Operador '{req.condicion}' inválido")
        try:
            mask = getattr(df[req.columna].astype(str), op)(req.valor)
        except Exception as e:
            raise HTTPException(400, f"Error: {e}")
    else:
        raise HTTPException(400, "Especificá valores o condición")
    elim = int(mask.sum())
    df = df[~mask]
    _guardar(nombre, df)
    _log(nombre, "DELETE", elim)
    return {"mensaje": f"{elim} registro(s) eliminado(s)", "eliminados": elim, "restantes": int(len(df))}

@router.post("/datasets/{nombre}/eliminar-por-id")
def eliminar_por_id(nombre: str, id: str = ""):
    if not id:
        raise HTTPException(400, "ID requerido")
    df = cargar_dataset(nombre)
    campo_id = _col(df, ["gbifID","id","occurrenceID","recordID"])
    if not campo_id:
        raise HTTPException(400, "No se detectó columna de ID")
    mask = df[campo_id].astype(str).str.strip() == id.strip()
    if not mask.any():
        raise HTTPException(404, f"ID '{id}' no encontrado")
    df = df[~mask]
    _guardar(nombre, df)
    _log(nombre, "DELETE", 1)
    return {"mensaje": "Registro eliminado", "eliminados": 1, "restantes": int(len(df))}

def _col(df, posibles):
    for c in posibles:
        if c in df.columns:
            return c
    return None
