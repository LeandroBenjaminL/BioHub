"""Escribe un registro en un archivo CSV."""

from pathlib import Path
import csv
from constantes import CODIFICACION
from utilidades.excepciones import ErrorDataset


def escribir_registro_csv(
    archivo: Path,
    columnas: list,
    registro: dict,
    delimitador: str = '\t'
) -> None:
    """
    Escribe un registro en un archivo CSV (o delimited).
    
    Si el archivo no existe, escribe el header primero.
    
    Parametros
    ----------
    archivo : Path
        Ruta del archivo de salida.
    columnas : list
        Lista de nombres de columnas (fieldnames).
    registro : dict
        Diccionario con los datos a escribir.
    delimitador : str
        Caracter separador de campos.
    
    Raises
    ------
    ErrorDataset
        Si no se puede escribir el archivo.
    """
    archivo_nuevo = not archivo.exists()

    try:
        with open(archivo, 'a', newline='', encoding=CODIFICACION) as f:
            writer = csv.DictWriter(f, fieldnames=columnas, delimiter=delimitador)
            if archivo_nuevo:
                writer.writeheader()
            writer.writerow(registro)
    except FileNotFoundError as e:
        raise ErrorDataset(f"No se pudo escribir el archivo de salida: {e}") from e
    except PermissionError as e:
        raise ErrorDataset(f"No se tiene permiso para escribir el archivo: {e}") from e
    except Exception as e:
        raise ErrorDataset(f"Error al escribir el registro: {e}") from e
