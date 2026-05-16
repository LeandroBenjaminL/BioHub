"""Paquete de utilidades para insertar registros."""

from utilidades.insertar.escribir import escribir
from utilidades.insertar.preparar_registro import preparar_registro
from utilidades.insertar.validar_registro import validar

__all__ = [
    'escribir',
    'preparar_registro',
    'validar',
]
