"""Funciones helper para generación automática de IDs."""
import csv
from pathlib import Path
from constantes import CODIFICACION, MODO_LECTURA
from utilidades.excepciones import ErrorDataset


def detectar_campo_id(columnas) -> str | None:
    """
    Detecta cuál es el campo de ID en el dataset.
    
    Parametros
    ----------
    columnas : list
        Lista de nombres de columnas del dataset.
    
    Retornos
    -------
    str
        Nombre del campo de ID encontrado, o None si no se detecta.
    """
    # Nombres comunes de ID en Darwin Core
    campos_id = ['gbifID', 'id', 'occurrenceID', 'recordID', 'identifier']

    for col in columnas:
        if col in campos_id:
            return col

    return None


def preparar_siguiente_id(original: Path, columnas: list,
                           delimitador: str) -> tuple[str | None, str]:
    """
    Detecta el campo ID y calcula el siguiente automáticamente.
    
    Parametros
    ----------
    original : Path
        Ruta al archivo del dataset.
    columnas : list
        Lista de nombres de columnas.
    delimitador : str
        Caracter separador.
    
    Retornos    
    -------
    tuple[str | None, str]
        (campo_id, siguiente_id). Si no hay campo_id, retorna (None, "").
    """
    campo_id = detectar_campo_id(columnas)
    if campo_id is None:
        return None, ""

    siguiente_id = calcular_siguiente_id(original, campo_id, delimitador)
    print(f"ID generado automáticamente: {siguiente_id}")
    return campo_id, siguiente_id


def calcular_siguiente_id(original: Path, campo_id: str, delimitador: str) -> str:
    """
    Calcula el siguiente ID automático basándose en el último registro.
    
    Lee el dataset original, obtiene el último ID y calcula el siguiente.
    Asume que los IDs son numéricos (entero autoincremental).
    
    Parametros
    ----------
    original : Path
        Ruta al archivo del dataset.
    campo_id : str
        Nombre del campo de ID.
    delimitador : str
        Caracter separador de campos.
    
    Retornos    
    -------
    str
        El siguiente ID como string.
    
    Raises
    ------
    ErrorDataset
        Si el archivo no existe o no se puede leer.
    """
    ultimo_id = 0

    try:
        with open(original, MODO_LECTURA, newline='', encoding=CODIFICACION) as f:
            lector = csv.DictReader(f, delimiter=delimitador)
            for fila in lector:
                if campo_id in fila and fila[campo_id].strip():
                    try:
                        id_actual = int(fila[campo_id])
                        if id_actual > ultimo_id:
                            ultimo_id = id_actual
                    except ValueError:
                        # Si no es número, usar 0
                        pass
    except FileNotFoundError as e:
        raise ErrorDataset(f"No se pudo leer el dataset: {original}") from e

    # El siguiente ID es el último + 1
    return str(ultimo_id + 1)
