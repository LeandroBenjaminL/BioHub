from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.analisis import router as analisis_router
from api.datasets import router as datasets_router
from api.busqueda import router as busqueda_router
from api.gestion import router as gestion_router

app = FastAPI(title="BioHub API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(analisis_router, prefix="/api")
app.include_router(datasets_router, prefix="/api", tags=["Datasets"])
app.include_router(busqueda_router, prefix="/api", tags=["Búsqueda"])
app.include_router(gestion_router, prefix="/api", tags=["Gestión"])

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "BioHub"}
