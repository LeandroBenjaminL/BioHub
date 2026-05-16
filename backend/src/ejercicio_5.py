"""Ejercicio 5 - Manipulación avanzada de datasets
En este ejercicio, se implementan funciones para buscar y actualizar registros en un dataset CSV.
Se incluyen:"""

import csv
from pathlib import Path
from constantes import CODIFICACION, DELIMITADOR_TAB, MODO_LECTURA, MODO_ESCRITURA, LOG
from utilidades.validaciones import detectar_campo_id
from ejercicio_3 import (
    validar_latitud, validar_longitud,
    fechas_invalidas, validar_country_code, validar_uncertainty
)
from ejercicio_7 import registrar_operacion

# Punto 5D
def validar_nuevo_valor(columna, valor):
    """valida un valor segun el tipo de columna.
    retorna True si es valido o si no hay validacion definida para esa columna
    """
    if columna in ('decimalLatitude', 'latitudeDecimal'):
        return validar_latitud(valor)
    if columna in ('decimalLongitude', 'longitudeDecimal'):
        return validar_longitud(valor)
    if columna == 'eventDate':
        return fechas_invalidas(valor) == 'Valida'
    if columna == 'countryCode':
        return validar_country_code(valor)
    if columna == 'coordinateUncertaintyInMeters':
        return validar_uncertainty(valor)
    return True


# Punto 5A
def buscar_por_columnas(original: Path, filtros: dict,
                         delimitador: str = DELIMITADOR_TAB) -> list[dict]:
    """
    Busca registros que coincidan con los filtros dados.
    
    Parametros
    ----------
    original : Path
        Ruta al archivo del dataset.
    filtros : dict
        Diccionario con columnas y valores a buscar.
        Ejemplo: {'occurrenceID': '123'} o {'countryCode': 'AR', 'stateProvince': 'Buenos Aires'}
    delimitador : str
        Caracter separador de campos.
    
    Retornos
    -------
    list[dict]
        Lista de registros que cumplen todos los filtros.
    """
    resultados = []

    try:
        with open(original, MODO_LECTURA, newline="", encoding=CODIFICACION) as dataset:
            lector = csv.DictReader(dataset, delimiter=delimitador)
            columnas = lector.fieldnames

            for col_filtro in filtros.keys():
                if col_filtro not in columnas:
                    print(f"ERROR: la columna {col_filtro} no existe en el dataset")
                    return []

            for fila in lector:
                coincide = True
                for col, valor in filtros.items():
                    if fila.get(col, "") != valor:
                        coincide = False
                        break
                if coincide:
                    resultados.append(fila)

    except FileNotFoundError:
        print(f"ERROR: no se encuentra el archivo {original}")
        return []

    return resultados

#Punto 5C
def actualizar_multiples_campos(original: Path, dataset_nombre : str, salida: Path, identificador: str,
                                 cambios: dict, delimitador= DELIMITADOR_TAB):
    """" Actualiza multiples campos de un registros en una sola operacion 
    Parametros
    ----------
    original : Path
        Ruta al archivo del dataset.
    salida : Path
        Ruta del archivo modificado.
    identificador : str
        Id del registro a modificar.
    cambios : dict
        Columnas con sus nuevos valores a cambiar.
        Ejemplo: {'countryCode' : 'BR', 'stateProvince' : 'Sao paulo'}.
    delimitador : str
        Caracter separador de campos.
    
    Retornos
    -------
    boolean
        True para modificacion exitosa, False para modificacion fallida.
    """

    # valido todos los cambios antes de tocar, 5D
    for col, valor in cambios.items():
        if not validar_nuevo_valor(col, valor):
            print(f"valor invalido para {col}")
            registrar_operacion(LOG, dataset_nombre, "UPDATE", 0, error=True)
            return False

    encontrado= False

    if original.resolve() == salida.resolve():
        print("ERROR: el archivo de salida debe ser distinto del original")
        registrar_operacion(LOG, dataset_nombre, "UPDATE", 0, error=True)
        return False
    try:
        with open(original, MODO_LECTURA, newline="", encoding=CODIFICACION) as dataset, \
             open(salida, MODO_ESCRITURA, newline="", encoding=CODIFICACION) as nuevo:
            lector = csv.DictReader(dataset, delimiter= delimitador)
            columnas = lector.fieldnames or []
            campo_id = detectar_campo_id(columnas)

            if campo_id is None:
                print("ERROR: no se detecto el id en el dataset")
                registrar_operacion(LOG, dataset_nombre, "UPDATE", 0, error=True)
                return False
            for col in cambios.keys():
                if col not in columnas:
                    print(f"ERROR: la columna {col} no existe en el dataset")
                    registrar_operacion(LOG, dataset_nombre, "UPDATE", 0, error=True)
                    return False

            escribir = csv.DictWriter(nuevo, fieldnames=columnas, delimiter=delimitador)
            escribir.writeheader()

            for fila in lector:
                if fila[campo_id] == identificador:
                    for col, valor in cambios.items():
                        fila[col] = valor
                    encontrado = True
                escribir.writerow(fila)

    except FileNotFoundError:
        print(f"ERROR: no se encuentra el archivo {original} o {salida}")
        registrar_operacion(LOG, dataset_nombre, "UPDATE", 0, error=True)
        return False

    if not encontrado:
        print(f"ERROR: no se encontro el registro con {campo_id} = {identificador}")
        registrar_operacion(LOG, dataset_nombre, "UPDATE", 0, error=True)
        return False

    print(f"Registro actualizado en {salida}")
    registrar_operacion(LOG, dataset_nombre, "UPDATE", 1)
    return True
