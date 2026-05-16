"""Ejercicio 6 - Eliminación de registros en datasets"""

from pathlib import Path
import csv

from constantes import CODIFICACION, DELIMITADOR_TAB, MODO_LECTURA, MODO_ESCRITURA,LOG 
from utilidades.insertar import validar
from utilidades.validaciones import detectar_campo_id,es_numero
from ejercicio_7 import registrar_operacion 

#Punto 6A
def eliminar_por_id(original: Path, salida: Path, dataset_nombre: str, identificador: str, delimitador=DELIMITADOR_TAB):
    """Elimina un registro del dataset dado su identificador.
    Si no encuentra el id, retorna False y reporta el error.

    Parametros
    ----------
    original : Path
        Ruta al archivo del dataset.
    salida : Path
        Ruta del archivo modificado.
    identificador : str
        Id del registro a eliminar.
    delimitador : str
        Caracter separador de campos.

    Retornos
    -------
    boolean
        True si se elimino, False si no se encontro el id.
    """
    encontrado = False

    with open(original, MODO_LECTURA, newline="", encoding=CODIFICACION) as dataset:
        with open(salida, MODO_ESCRITURA, newline="", encoding=CODIFICACION) as nuevo:
            lector = csv.DictReader(dataset, delimiter=delimitador)
            columnas = lector.fieldnames or []
            campo_id = detectar_campo_id(columnas)
            if campo_id is None:
                print("ERROR: no se detecto columna de ID en el dataset")
                registrar_operacion(LOG, dataset_nombre, "DELETE", 0, error=True)
                return False
            escritor = csv.DictWriter(nuevo, fieldnames=columnas, delimiter=delimitador)
            escritor.writeheader()
            for fila in lector:
                if fila[campo_id] == identificador:
                    encontrado = True
                else:
                    escritor.writerow(fila)
    cantidad = 1 if encontrado else 0
    registrar_operacion(LOG, dataset_nombre, "DELETE", cantidad)
    if not encontrado:
        print(f"no se encontro el registro con {campo_id} = {identificador}")
        return False
    return True


#Punto 6B
def eliminar_registros_por_columna(original : Path, salida: Path, dataset_nombre: str, col: str,
                                    valores: list, delimitador = DELIMITADOR_TAB):
    """ Elimina registros cuyo valores en la columna indicada coincidan con alguno
      de la lista que llega como parametro 
    Parametros
    ----------
    original : Path
        Ruta al archivo del dataset.
    salida : Path
        Ruta del archivo modificado.
    col : str
        Nombre de la columna de interes donde se eliminaran los valores recibidos
    valores : list
        Conjunto de valores a eliminar en la columna recibida
    delimitador : str
        Caracter separador de campos.
    
    Retornos
    -------
    boolean
        True para eliminacion exitosa, False para eliminacion fallida.
    """
    eliminados = 0
    try:
        with open(original, MODO_LECTURA, newline="", encoding=CODIFICACION) as dataset, \
             open(salida, MODO_ESCRITURA, newline="", encoding=CODIFICACION) as nuevo:
            lector = csv.DictReader(dataset, delimiter= delimitador)
            columnas = lector.fieldnames or []

            if col not in columnas:
                print(f"ERROR: la columna {col} no existe en el dataset")
                return False
            escribir = csv.DictWriter(nuevo, fieldnames=columnas, delimiter=delimitador)
            escribir.writeheader()

            #Normaliza para evitar problemas de formato
            valores_normalizados={v.strip().lower() for v in valores}
            for fila in lector:
                #Si el valor de la columna no coincide con los buscados lo deja
                if fila[col].strip().lower() not in valores_normalizados:
                    escribir.writerow(fila)
                else:
                    eliminados +=1

    except FileNotFoundError:
        print(f"ERROR: no se encuentra el archivo {original} o {salida}")
        return False
    registrar_operacion(LOG, dataset_nombre, "DELETE", eliminados)
    print(f"Registro actualizado en {salida}")
    return True

#Punto 6c
def registro_condicion(registro : str, condicion : str, valor : str):
    """Recibe un registro, una condicion y un valor. Retorna Verdadero si 
    ese registro deberia eliminarse o no"""
    if es_numero(registro) and es_numero(valor):
        r = float(registro)
        v = float(valor)
    elif es_numero(registro):
        r = float(registro)
        v = float(valor) if es_numero(valor) else 0
    elif es_numero(valor):
        r = float(registro) if es_numero(registro) else 0
        v = float(valor)
    else:
        r = registro
        v = valor

    if condicion == "!=" and r != v:
        return True
    elif condicion == "==" and r == v:
        return True
    elif condicion == ">" and r > v:
        return True
    elif condicion == ">=" and r >= v:
        return True
    elif condicion == "<" and r < v:
        return True
    elif condicion =="<=" and r <= v:
        return True
    return False

def eliminar_registro_condicion (original : Path, salida : Path, dataset_nombre: str, col : str,
                                  condicion : str, valor : str, delimitador =DELIMITADOR_TAB):
    """Recibe una columna, una condicion y un valor.
    Aplica la condicion con el valor a cada campo, si retorna True se debe eliminar"""

    operadores = ["!=", "==", ">", ">=", "<", "<="]
    if condicion not in operadores:
        print(f"Error operador: {condicion} no valido")
        return False
    if not isinstance(valor, str):
        print(f"El valor que desea comparar, {valor}, no es compatible")
        return False
    eliminados = 0
    try:
        with open(original, MODO_LECTURA,newline='', encoding=CODIFICACION) as dataset, \
            open(salida,MODO_ESCRITURA,newline='',encoding=CODIFICACION) as dataset_salida:
            lector = csv.DictReader(dataset, delimiter=delimitador)
            # Validar que el CSV no esté vacío y tenga encabezados
            if not lector.fieldnames:
                print("Error: el archivo está vacío o mal formado")
                return False
            columnas = lector.fieldnames
            if col not in columnas:
                print(f"Error: columna '{col}' no está en el archivo")
                return False
            escritor = csv.DictWriter(dataset_salida, fieldnames=columnas, delimiter=delimitador)
            escritor.writeheader()

            for fila in lector:
                if not registro_condicion(fila[col],condicion,valor):
                    escritor.writerow(fila)
                else: 
                    eliminados += 1

    except FileNotFoundError:
        print(f"ERROR: no se encuentra el archivo {original} o {salida}")
        return False
    registrar_operacion(LOG, dataset_nombre, "DELETE", eliminados)
    print(f"Registro actualizado en {salida}")
    return True



#punto 6E
def sanitizar_dataset(data_nombre: str, original: Path, salida: Path, delimitador=DELIMITADOR_TAB):
    """Sanitiza un dataset a partir de nombre.
      -Lee el dataset original y descarta los que no pasan las validaciones.
      -gegenere un nuevo archivo en processed_datasets.
    """
    eliminados = 0 
    try:
        with open(original, MODO_LECTURA, newline="", encoding=CODIFICACION) as dataset, \
             open(salida, MODO_ESCRITURA, newline="", encoding= CODIFICACION) as nuevo:
            lector = csv.DictReader(dataset, delimiter=delimitador)
            columnas = lector.fieldnames or []

            escritor = csv.DictWriter(nuevo, fieldnames=columnas, delimiter=delimitador)
            escritor.writeheader()

            for fila in lector:
                if validar(fila)[0]:
                    escritor.writerow(fila)
                else: 
                    eliminados += 1
    except FileNotFoundError:
        print(f"ERROR: no se encontro el archivo {original} o {salida}")
        return False
    registrar_operacion(LOG, data_nombre ,"DELETE", eliminados)
    print(F"Dataset {data_nombre} sanitizado en {salida}")
    return True

#punto 6F
def eliminar_registros_con_reporte(original: Path, salida: Path, dataset_nombre: str, col: str,
                                   valores: list, delimitador=DELIMITADOR_TAB):
    """Elimina registros cuyo valor en columna 'col' coincida con algún valor en 'valores'.
    Devuelve cantidad eliminada, porcentaje, y lista con motivos detallados.

    Parámetros:
    - original: archivo CSV origen
    - salida: archivo CSV destino
    - col: columna para filtrar
    - valores: lista de valores para eliminar
    - delimitador: separador CSV

    Retorna:
    - cantidad_eliminados: int
    - porcentaje_eliminados: float
    - lista_motivos: list de dict con detalles del registro eliminado
    """
    cantidad_total = 0
    cantidad_eliminados = 0
    lista_motivos = []

    with open(original, MODO_LECTURA, newline='', encoding=CODIFICACION) as f_origen, \
         open(salida, MODO_ESCRITURA, newline='', encoding=CODIFICACION) as f_salida:
        lector = csv.DictReader(f_origen, delimiter=delimitador)
        columnas = lector.fieldnames or []

        if col not in columnas:
            print(f"ERROR: Columna '{col}' no existe en el archivo.")
            registrar_operacion(LOG, dataset_nombre, "DELETE", 0, error=True)
            return 0, 0.0, []

        escritor = csv.DictWriter(f_salida, fieldnames=columnas, delimiter=delimitador)
        escritor.writeheader()

        for fila in lector:
            cantidad_total += 1
            valor = fila.get(col, '')
            if valor in valores:
                cantidad_eliminados += 1
                motivo = {'registro': fila, 'motivo': f"Valor '{valor}' en columna '{col}'"}
                lista_motivos.append(motivo)
            else:
                escritor.writerow(fila)

    porcentaje_eliminados = (cantidad_eliminados / cantidad_total * 100) if cantidad_total else 0
    registrar_operacion(LOG, dataset_nombre, "DELETE", cantidad_eliminados)
    return cantidad_eliminados, porcentaje_eliminados, lista_motivos
