"""Funciones helper para obtener y validar datos del dataset."""

import csv
from pathlib import Path
from utilidades.excepciones import ErrorColumnas

# Constante replicada de src.constantes (para evitar dependencias)
CODIFICACION = 'UTF-8'

def obtener_columnas_seguras(original: Path, delimitador: str) -> list:
    """
    Obtiene las columnas del dataset con validación.
    Es autosuficiente - no depende de otros módulos.
    
    Argumentos
    ---------:
        original: ruta al archivo del dataset.
        delimitador: caracter separador de campos.
    
    Retornos:
        Lista con los nombres de las columnas.
    
    Raises:
        ErrorColumnas: si no se pueden obtener las columnas.
    """
    with open(original, 'r', encoding=CODIFICACION) as f:
        reader = csv.DictReader(f, delimiter=delimitador)
        columnas = reader.fieldnames

        if columnas is None or len(columnas) == 0:
            raise ErrorColumnas(f"No se pudieron obtener columnas de {original}")

        return list(columnas)
