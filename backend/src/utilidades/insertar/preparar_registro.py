"""Prepara el registro completo con el ID asignado."""

from pathlib import Path
from utilidades.validaciones import obtener_columnas_seguras as obtener_columnas
from utilidades.validaciones import detectar_campo_id, calcular_siguiente_id

def preparar_registro(
    datos: dict,
    original: Path,
    delimitador: str = '\t'
) -> dict:
    """
    Prepara el registro completo con el ID automático.

    Parametros
    ----------
    datos : dict
        Diccionario con los datos del registro (sin ID).
    original : Path
        Ruta al archivo del dataset original.
    delimitador : str
        Caracter separador de campos (por defecto TAB).

    Retornos
    -------
    dict
        Diccionario completo con el ID incluido.
    """
    columnas = obtener_columnas(original, delimitador)
    if not columnas:
        return datos

    campo_id = detectar_campo_id(columnas)
    if campo_id is None:
        return datos

    # Calcular siguiente ID

    siguiente_id = calcular_siguiente_id(original, campo_id, delimitador)

    # Agregar ID al registro
    resultado = datos.copy()
    resultado[campo_id] = siguiente_id

    return resultado
