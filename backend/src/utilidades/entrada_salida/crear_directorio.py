"""Crea un directorio de forma segura."""

from pathlib import Path
from utilidades.excepciones import ErrorDataset


def crear_directorio_seguro(ruta: Path) -> None:
    """
    Crea un directorio si no existe.
    
    Parametros
    ----------
    ruta : Path
        Ruta del directorio a crear.
    
    Raises
    ------
    ErrorDataset
        Si no se puede crear el directorio.
    """
    try:
        ruta.mkdir(exist_ok=True)
    except PermissionError as e:
        raise ErrorDataset(f"No se tiene permiso para crear la carpeta: {e}") from e
    except Exception as e:
        raise ErrorDataset(f"Error al crear la carpeta: {e}") from e
