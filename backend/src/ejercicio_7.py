""" Ejercicio 7 - Registro de operaciones """

from pathlib import Path
from datetime import datetime
from constantes import CODIFICACION, MODO_AGREGAR

#Punto 7A
def obtener_fecha_hora_actual(formato: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Retorna la fecha y hora actual formateada según el string de formato dado.
    Por defecto devuelve formato: YYYY-MM-DD HH:MM:SS"""
    ahora = datetime.now()
    return ahora.strftime(formato)


#Punto 7B
def registrar_operacion(log_path: Path, dataset: str, operacion: str, cantidad: int, error: bool = False):
    """ Registra una operacion en el archivo de log.

    Parametros
    ----------
    log_path : Path
        Ruta al archivo del log.
    dataset : str
        Nombre del dataset modificado.
    operacion : str
        Operacion realizada en el dataset indicado.
    cantidad : int
        Cantidad de registros afectados en el dataset indicado.
    error : bool
        Si True, agrega "| ERROR" al final de la linea. Por defecto False.

    Retornos
    ----------
    boolean
        False en caso de que la operacion no sea valida, True si se guardo correctamente

    """
    # Normaliza
    operacion=operacion.upper()

    # Da error si la operacion no es una de las 3 validas
    if operacion not in {"INSERT", "UPDATE", "DELETE"}:
        print("ERROR: operación inválida")
        return False

    fecha_hora=obtener_fecha_hora_actual()

    linea= f"{fecha_hora} | {dataset} | {operacion} | {cantidad}"
    if error or cantidad ==0:
        linea += " | ERROR"
    else:
        linea += " | OK"

    linea += "\n"

    with open(log_path, MODO_AGREGAR, encoding= CODIFICACION) as log:
        log.write(linea)

    print(f"Operacion agregada en {log_path}")
    return True