"""Paquete de validaciones."""

from utilidades.validaciones.generar_ids import (
    detectar_campo_id,
    calcular_siguiente_id,
    preparar_siguiente_id,
)
from utilidades.validaciones.coordenadas_validadas import coordenadas_validas
from utilidades.validaciones.es_numero import es_numero
from utilidades.validaciones.obtener_datos import obtener_columnas_seguras

__all__ = [
    'detectar_campo_id',
    'calcular_siguiente_id',
    'preparar_siguiente_id',
    'obtener_columnas_seguras',
    'coordenadas_validas',
    'es_numero'
]
