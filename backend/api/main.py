from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.analisis import router as analisis_router
from api.datasets import router as datasets_router
from api.busqueda import router as busqueda_router
from api.gestion import router as gestion_router
from pathlib import Path

app = FastAPI(title="BioHub API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(analisis_router, prefix="/api")
app.include_router(datasets_router, prefix="/api", tags=["Datasets"])
app.include_router(busqueda_router, prefix="/api", tags=["Búsqueda"])
app.include_router(gestion_router, prefix="/api", tags=["Gestión"])

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "BioHub"}

@app.get("/api/logs")
def logs():
    log_path = Path(__file__).parent.parent.parent / "logs" / "operations.log"
    if not log_path.exists():
        return {"lineas": [], "total": 0, "resumen": {}}
    lines = log_path.read_text(encoding="UTF-8").strip().split("\n")
    lines = [l for l in lines if l.strip()]
    ins = sum(1 for l in lines if "INSERT" in l)
    upd = sum(1 for l in lines if "UPDATE" in l)
    dele = sum(1 for l in lines if "DELETE" in l)
    err = sum(1 for l in lines if "ERROR" in l)
    return {
        "total": len(lines),
        "lineas": lines[-200:],
        "resumen": {"INSERT": ins, "UPDATE": upd, "DELETE": dele, "ERROR": err},
    }
