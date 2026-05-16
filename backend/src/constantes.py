"""Constantes utilizadas en el proyecto."""
from pathlib import Path
CODIFICACION = 'UTF-8'
DELIMITADOR_TAB = '\t'
MODO_LECTURA = 'r'
MODO_ESCRITURA = 'w'
MODO_AGREGAR = 'a'

# Ruta al proyecto (biohub/)
PROYECTO = Path(__file__).parent.parent.parent

# Rutas de datasets originales
DATA1 = PROYECTO/"datasets"/"IADIZA"/"occurrence.txt"
DATA2 = PROYECTO/"datasets"/"iNaturalist"/"observations.csv"
DATA3 = PROYECTO/"datasets"/"Xeno-canto"/"Occurrence.txt"

# Ruta de salida para datasets procesados
RUTA_PROCESADOS = PROYECTO / "datasets_procesados"
#Punto 3C

IADIZA={
        'Nombre':'IADIZA',
        'Path' : DATA1,
        'Delimitador' : '\t'
        }
XENO_CANTO ={
            'Nombre':'Xeno-canto',
            'Path' : DATA3,
            'Delimitador' : ','
            }
INATURALIST={
            'Nombre':'iNaturalist',
            'Path' : DATA2,
            'Delimitador' : ','
            }

LISTA_DATASETS = [
    {
        'Nombre':'IADIZA',
        'Path' : DATA1,
        'Delimitador' : '\t'
    },
    {
        'Nombre':'iNaturalist',
        'Path' : DATA2,
        'Delimitador' : ','
    },
    {
        'Nombre':'Xeno.canto',
        'Path' : DATA3,
        'Delimitador' : ','
    }
]

#3H
LAT_MIN_SUDAMERICA = -56.0
LAT_MAX_SUDAMERICA = 13.0
LON_MIN_SUDAMERICA = -82.0
LON_MAX_SUDAMERICA = -31.0
#3F
MAX = 100

# Ruta de operations.log
LOG=PROYECTO/"logs"/"operations.log"