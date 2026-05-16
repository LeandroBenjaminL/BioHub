""" Procesar un registro. """
from constantes import DELIMITADOR_TAB
from utilidades.insertar import escribir 
from utilidades.entrada_salida.pedir_datos import pedir_datos_por_columna as pedir_datos
from utilidades.insertar import validar
from pathlib import Path

def procesar_un_registro(
    columnas: list,
    campo_id: str,
    id_actual: str,
    dataset_nombre: str,
    delimitador: str = DELIMITADOR_TAB
) -> bool:
    """
    Pide datos, valida y escribe un registro.
    
    Parametros
    ----------
    columnas : list
        Lista de columnas del dataset.
    campo_id : str
        Nombre del campo de ID (ej: gbifID).
    id_actual : str
        id a asignar al registro.
    dataset_nombre : str
        Nombre del archivo de salida.
    delimitador : str
        Caracter separados de campos.
    
    Retornos
    -------
    bool
        True si se insertó OK, False si falló la validación.
    """
    # 1. Pedir datos al usuario
    registro = pedir_datos(columnas, campo_id, id_actual) 
    # 2. Validar
    estatus, errores = validar(registro)
    if not estatus:
        print("ERROR: registro inválido")
        print(errores)
        return False

    # 3. Escribir
    escribir(columnas, registro, dataset_nombre, delimitador)
    print("Registro insertado")
    return True
