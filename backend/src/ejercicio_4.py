"""Módulo de ejercicio 4 - Inserción de registros."""

from pathlib import Path

from utilidades.insertar import validar
from utilidades.entrada_salida.procesar_registro import procesar_un_registro
from utilidades.validaciones import detectar_campo_id, calcular_siguiente_id, preparar_siguiente_id
from utilidades.excepciones import ErrorDataset, ErrorColumnas

from constantes import DELIMITADOR_TAB, LOG
from ejercicio_2 import obtener_columnas_ejercicio_2 as obtener_columnas
from ejercicio_7 import registrar_operacion


#Punto 4A y 4B
def fila_vacia(original: Path, delimitador=DELIMITADOR_TAB):
    """Crea un DICCIONARIO, con un registro vacio para cada columna (menos el ID)
        Argumentos: Path del dataset, delimitador del mismo
        Retorna: Un diccionario vacio; key = columna; valores = vacio
    """
    diccionario = {}
    columnas = obtener_columnas(original,delimitador)
    for elem in columnas[1:]:
        diccionario[elem] = ""

    return diccionario

#Punto 4C
def validar_imprimir(registro: dict):
    """ Valida un registro antes de insertarlo.
      -Reutiliza funciones del ejercicio 3.
      -Imprime los errores encontrados.
      -Retorna True si el registro es valido, False caso contrario
    """
    valido, errores = validar(registro)
    for error in errores:
        print(f"ERROR: {error}")
    return valido


# Punto 4D - Retornar registro listo para CSV (con ID)
def preparar_registro(original: Path, datos: dict, delimitador: str = DELIMITADOR_TAB) -> dict:
    """
    Prepara el registro completo con el ID automático.

    Parametros
    ----------
    original : Path
        Ruta al archivo del dataset.
    datos : dict
        Diccionario con los datos del registro (sin ID).
    delimitador : str
        Caracter separador de campos.

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

    siguiente_id = calcular_siguiente_id(original, campo_id, delimitador)

    resultado = datos.copy()
    resultado[campo_id] = siguiente_id

    return resultado


# Punto 4F - Flujo completo de inserción
def insertar_registro(
    original: Path,
    dataset_nombre: str,
    delimitador: str = DELIMITADOR_TAB
) -> bool:
    """
    Inserta un solo registro en el dataset.
    
    Parametros
    ----------
    original : Path
        Ruta al archivo original.
    dataset_nombre : str
        Nombre del archivo de salida.
    delimitador : str
        Caracter separador de campos.
    
    Retorna
    -------
    bool
        True si se insertó OK, False si falló.
    
    Raises
    ------
    ErrorColumnas
        Si no se pueden obtener las columnas.
    ErrorDataset
        Si falla al preparar el ID.
    """
    # 1. Obtener columnas
    try:
        columnas = obtener_columnas(original, delimitador)
    except ErrorColumnas as e:
        print(f"ERROR: {e}")
        registrar_operacion(LOG, dataset_nombre, "INSERT", 0, error=True)
        return False
    # 2. Preparar ID
    try:
        campo_id, siguiente_id = preparar_siguiente_id(original, columnas, delimitador)
        if campo_id is None:
            print("ERROR: No se detectó campo de ID")
            registrar_operacion(LOG, dataset_nombre, "INSERT", 0, error=True)
            return False
    except ErrorDataset as e:
        print(f"ERROR: {e}")
        registrar_operacion(LOG, dataset_nombre, "INSERT", 0, error=True)
        return False
    # 3. Procesar (pedir + validar + escribir)
    try:
        if procesar_un_registro(columnas, campo_id, siguiente_id, dataset_nombre, delimitador):
            registrar_operacion(LOG, dataset_nombre, "INSERT", 1)
            return True
    except Exception as e:
        print(f"ERROR: {e}")
        registrar_operacion(LOG, dataset_nombre, "INSERT", 0, error=True)
        return False
    
    registrar_operacion(LOG, dataset_nombre, "INSERT", 0, error=True)
    return False

# Punto 4G
def insertar_registros(original: Path, dataset_nombre: str,
                        delimitador: str = DELIMITADOR_TAB) -> int:
    """
    Inserta varios registros en una sola operación.
    Pide registros hasta que el usuario dice que no.
    
    Parametros
    ----------
    original : Path
        Ruta al archivo original.
    dataset_nombre : str
        Nombre del archivo de salida.
    delimitador : str
        Caracter separador de campos.
    
    Retornos
    -------
    int
        Cantidad de registros insertados correctamente.
    """
    try:
        columnas = obtener_columnas(original, delimitador)
        campo_id, siguiente_id = preparar_siguiente_id(original, columnas, delimitador)
    except (ErrorColumnas, ErrorDataset) as e:
        print(f"ERROR: {e}")
        registrar_operacion(LOG, dataset_nombre, "INSERT", 0, error=True)
        return 0
    if campo_id is None:
        print("ERROR: No se detectó campo de ID")
        registrar_operacion(LOG, dataset_nombre, "INSERT", 0, error=True)
        return 0
    insertados = 0
    errores = 0
    while True:
        try:
            id_actual = str(int(siguiente_id) + insertados)
        except ValueError:
            print(f"ERROR: el ID '{siguiente_id}' no es numerico, no se puede auto-generar")
            registrar_operacion(LOG, dataset_nombre, "INSERT", 0, error=True)
            return insertados
        if procesar_un_registro(columnas, campo_id, id_actual, dataset_nombre, delimitador):
            insertados += 1
        else:
            errores += 1
        if input("otro? s/n: ").strip().lower() not in ('s', 'si', 'y', 'yes'):
            break
    
    if errores != 0:
        registrar_operacion(LOG, dataset_nombre, "INSERT", errores, error=True)
    if insertados>0:
        registrar_operacion(LOG, dataset_nombre, "INSERT", insertados)
    
    return insertados
