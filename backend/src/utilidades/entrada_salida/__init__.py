"""Paquete de entrada y salida (I/O)."""

from utilidades.entrada_salida.pedir_datos import pedir_datos_por_columna
from utilidades.entrada_salida.crear_directorio import crear_directorio_seguro
from utilidades.entrada_salida.escribir import escribir_registro_csv
from utilidades.entrada_salida.procesar_registro import procesar_un_registro

# Alias más limpio
pedir_datos = pedir_datos_por_columna

__all__ = [
    'pedir_datos',
    'pedir_datos_por_columna',
    'crear_directorio_seguro',
    'escribir_registro_csv',
    'procesar_un_registro',
]