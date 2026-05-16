# BioHub

Sistema de análisis y visualización de datos de biodiversidad en formato Darwin Core. Procesa y consulta datasets de **IADIZA**, **iNaturalist** y **Xeno-canto** mediante una API REST con FastAPI y un frontend SPA vanilla.

## Arquitectura

```
┌──────────────┐     HTTP      ┌──────────────────┐     pandas     ┌──────────────────┐
│  Frontend     │ ←──────────→ │  FastAPI Backend  │ ←───────────→ │  CSV datasets     │
│  index.html   │   :4321      │  uvicorn :8000    │               │  (Darwin Core)    │
│  Chart.js     │              │                   │               │                   │
│  Leaflet      │              │  /api/*           │               │  datasets/        │
└──────────────┘              └──────────────────┘               │  datasets_proc/   │
                                                                 └──────────────────┘
```

## Stack

| Capa     | Tecnología                                                       |
| -------- | ---------------------------------------------------------------- |
| Backend  | Python 3.14+, FastAPI, Pandas, Uvicorn                           |
| Frontend | HTML/CSS/JS vanilla, Chart.js (CDN), Leaflet (CDN)              |
| Datos    | Darwin Core CSV (IADIZA, iNaturalist, Xeno-canto)               |

## Datos

| Dataset       | Registros | Coordenadas | Fuente                              |
| ------------- | --------- | ----------- | ----------------------------------- |
| **IADIZA**    | ~2.370    | 0%          | Instituto Argentino de Investigación |
| **iNaturalist** | ~800 MB  | ~90%        | iNaturalist.org                     |
| **Xeno-canto** | ~10.000   | N/A         | xeno-canto.org (audios de aves)     |

## API Endpoints

### Health

| Método | Ruta         | Descripción                    |
| ------ | ------------ | ------------------------------ |
| GET    | `/api/health`| Estado del servidor            |

### Datasets

| Método | Ruta                                          | Descripción                                      |
| ------ | --------------------------------------------- | ------------------------------------------------ |
| GET    | `/api/datasets`                               | Lista todos los datasets disponibles             |
| GET    | `/api/datasets/{nombre}`                      | Info de un dataset (filas, columnas, tamaño)     |
| GET    | `/api/datasets/{nombre}/columnas`             | Columnas + tipo de datos (lee 1 fila)            |
| GET    | `/api/datasets/{nombre}/resumen-columnas`     | % de nulos por columna (lee 1000 filas)          |
| GET    | `/api/datasets/{nombre}/docs`                 | Diccionario de datos del dataset                 |
| GET    | `/api/datasets/comparativa`                   | Comparación entre datasets (por estimación)      |

### Gráficos

| Método | Ruta                                                  | Descripción                     |
| ------ | ----------------------------------------------------- | ------------------------------- |
| GET    | `/api/datasets/{nombre}/graficos/por-pais`            | Registros agrupados por país    |
| GET    | `/api/datasets/{nombre}/graficos/por-ano`             | Registros por año               |
| GET    | `/api/datasets/{nombre}/graficos/taxonomia`           | Distribución taxonómica         |
| GET    | `/api/datasets/{nombre}/graficos/completitud`         | Calidad/completitud de datos    |

### Búsqueda

| Método | Ruta                                    | Descripción                        |
| ------ | --------------------------------------- | ---------------------------------- |
| GET    | `/api/datasets/{nombre}/buscar?q=`      | Búsqueda textual en el dataset     |
| GET    | `/api/datasets/{nombre}/mapa`           | Datos geo-ubicables para Leaflet   |

### Gestión (CRUD)

| Método | Ruta                   | Descripción                        |
| ------ | ---------------------- | ---------------------------------- |
| POST   | `/api/gestion/insertar`| Inserta un registro                |
| PUT    | `/api/gestion/actualizar`| Actualiza un registro            |
| DELETE | `/api/gestion/eliminar`| Elimina un registro                |

### Logs

| Método | Ruta       | Descripción            |
| ------ | ---------- | ---------------------- |
| GET    | `/api/logs`| Historial de consultas |

## Frontend — 7 secciones

La interfaz es una **SPA de una sola página** (`index.html`) con navegación por sidebar:

| Sección       | Descripción                                              |
| ------------- | -------------------------------------------------------- |
| **Inicio**    | Dashboard general con cards de resumen                   |
| **Estado**    | Health check + estado de cada dataset                    |
| **Búsqueda**  | Búsqueda textual en los datasets                         |
| **Visualización** | Gráficos (barras, taxonomía, completitud) + mapa Leaflet |
| **Gestión**   | CRUD: insertar, actualizar, eliminar registros           |
| **Datasets**  | Lista de datasets con columnas y nulls                   |
| **Ficha**     | Detalle de un registro individual                        |

## Arranque rápido

```bash
# 1. Backend
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000

# 2. Frontend (en otra terminal)
cd frontend
python3 -m http.server 4321

# 3. Abrir http://localhost:4321
```

## Variables de entorno

```bash
# .env (ver .env.example)
BACKEND_PORT=8000
FRONTEND_PORT=4321
```

## Estructura del proyecto

```
biohub/
├── backend/
│   ├── api/
│   │   ├── main.py           # App FastAPI + CORS + routers
│   │   ├── datasets.py       # Endpoints de datasets
│   │   ├── analisis.py       # Endpoints de gráficos
│   │   ├── busqueda.py       # Búsqueda textual
│   │   └── gestion.py        # CRUD
│   ├── src/
│   │   ├── ejercicio_2.py .. _7.py  # Lógica de procesamiento
│   │   ├── constantes.py     # Configuración global
│   │   ├── codigos_paises.py # Códigos ISO de países
│   │   └── utilidades/       # Validaciones, I/O, inserción
│   └── requirements.txt
├── frontend/
│   └── index.html            # SPA (Chart.js + Leaflet)
├── datasets/                 # Datos crudos (symlink)
├── datasets_procesados/      # Datos procesados
├── logs/                     # Logs de consultas
├── .env.example
├── .gitignore
└── README.md
```

## Optimizaciones

- Los endpoints de análisis leen **máximo 2000 filas** para evitar saturar el servidor con iNaturalist (800 MB)
- La detección de columnas lee **1 fila**
- La comparativa entre datasets usa **estimación por tamaño de archivo** (~0.3s en vez de 30s+)
- Los datos geo-ubicables se sirven como GeoJSON simplificado
