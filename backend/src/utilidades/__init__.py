"""Paquete de utilidades."""

# Apenas los módulos que existen actualmente
from utilidades.entrada_salida import (
    pedir_datos_por_columna as pedir_datos,
    crear_directorio_seguro,
    escribir_registro_csv,
    procesar_un_registro,
)

from utilidades.validaciones import obtener_columnas_seguras

from utilidades.insertar import (
    escribir,
    preparar_registro,
    validar_registro,
)

from utilidades.excepciones import ErrorColumnas, ErrorDataset


__all__ = [
    # entrada_salida
    'pedir_datos',
    'crear_directorio_seguro',
    'escribir_registro_csv',
    'procesar_un_registro',
    # validaciones
    'obtener_columnas_seguras',
    # insertar
    'escribir',
    'preparar_registro',
    'validar_registro',
    # excepciones
    'ErrorColumnas',
    'ErrorDataset',
]
