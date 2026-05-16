"""Escribe el registro en el archivo de salida."""

from pathlib import Path
from utilidades.entrada_salida import (
    crear_directorio_seguro,
    escribir_registro_csv,
)
from constantes import RUTA_PROCESADOS


def escribir(
    columnas: list,
    registro: dict,
    dataset_nombre: str,
    delimitador: str = '\t'
) -> Path:
    """
    Escribe el registro en processed_datasets.
    
    Parameters
    ----------
    columnas : list
        Lista de nombres de columnas.
    registro : dict
        Diccionario con los datos.
    dataset_nombre : str
        Nombre del archivo.
    delimitador : str
        Caracter separador.
    
    Returns
    -------
    Path
        Ruta del archivo escrito.
    
    Raises
    ------
    ErrorDataset
        Si no se puede escribir.
    """
    output_dir = RUTA_PROCESADOS
    crear_directorio_seguro(output_dir)

    output_path = output_dir / f"{dataset_nombre}.txt"
    escribir_registro_csv(output_path, columnas, registro, delimitador)

    return output_path
