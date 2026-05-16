"""
Módulo de lectura y análisis de datasets Darwin Core.

Este módulo contiene funciones para explorar archivos CSV
provenientes de registros de biodiversidad.
"""

import csv
from collections import Counter
from pathlib import Path
from utilidades.excepciones import ErrorColumnas
from constantes import CODIFICACION, DELIMITADOR_TAB, MODO_LECTURA



# Punto A
def imprimir10_filas(original:Path, x:int, delimitador= DELIMITADOR_TAB)-> None:
    """
    Imprime las primeras x filas del dataset.

    Args:
        original: ruta al archivo del dataset.
        x: cantidad de filas a imprimir.
        delimitador: caracter separador de campos (por defecto TAB).
    """
    with open(original, MODO_LECTURA, newline= "", encoding=CODIFICACION)  as dataset:
        diccionario = csv.DictReader(dataset, delimiter=delimitador)
        for _ in range(x):
            try:
                fila = next(diccionario)
                print(list(fila.values()))
            except StopIteration:
                print(f"(el dataset tiene menos de {x} filas)")
                break



# Punto B
def obtener_columnas_ejercicio_2(original: Path, delimitador: str = '\t') -> list[str]:
    """
    Obtiene las columnas de un dataset.
    
    Parametros
    ----------
    original : Path
        Ruta al archivo del dataset.
    delimitador : str
        Caracter separador de campos.
    
    Retornos
    -------
    list[str]
        Lista de nombres de columnas.
    
    Raises
    ------
    ErrorColumnas
        Si no se pueden obtener las columnas.
    """
    try:
        with open(original, 'r', encoding=CODIFICACION) as f:
            reader = csv.DictReader(f, delimiter=delimitador)
            columnas = reader.fieldnames
            if not columnas:
                raise ErrorColumnas(f"No se pudieron obtener columnas de {original}")
            return list(columnas)
    except FileNotFoundError as e:
        raise ErrorColumnas(f"Archivo no encontrado: {original}") from e



# Punto C
def posicion_columnas(original:Path, delimitador=DELIMITADOR_TAB)-> dict:
    """
    Retorna la posición (índice) de cada columna en el dataset.

    Args:
        original: ruta al archivo del dataset.
        delimitador: caracter separador de campos (por defecto TAB).

    Returns:
        Diccionario {nombre_columna: indice} para cada columna.
    """
    with open(original, MODO_LECTURA, newline= "", encoding=CODIFICACION) as archivo:

        csv_reader=csv.reader(archivo, delimiter=delimitador)
        header=next(csv_reader)
        indices={}

        for indice, columna in enumerate(header):
            indices[columna]=indice

        return indices



# Punto D
def contar_filas(original, delimitador=DELIMITADOR_TAB):
    """Cuenta la cantidad total de filas del dataset."""
    with open(original, MODO_LECTURA, newline="", encoding=CODIFICACION) as archivo:
        lector = csv.DictReader(archivo, delimiter=delimitador)
        return sum(1 for _ in lector)

# Punto E
def columnas_con_nulos(original:Path, delimitador=DELIMITADOR_TAB)-> list:
    """
    Retorna columnas con al menos un dato nulo.

    Args:
        original: ruta al archivo del dataset.
        delimitador: caracter separador de campos (por defecto TAB).

    Returns:
        Lista de columnas con al menos un valor nulo.
    """
    # Se delega el cálculo a registros_vacios para mantener la consistencia
    # y evitar la duplicación de lógica de procesamiento de archivos.
    vacios = registros_vacios(original,delimitador)
    return[col for col, pct in vacios.items() if pct > 0]


# Punto F
def registros_vacios(original:Path, delimitador=DELIMITADOR_TAB)-> dict:
    """
    Calcula el porcentaje de registros nulos por cada columna.

    Args:
        original: ruta al archivo del dataset.
        delimitador: caracter separador de campos (por defecto TAB).

    Returns:
        Diccionario {columna: porcentaje_nulos} para cada columna.
    """
    # Se opta por csv.reader para mapear índices manualmente con enumerate
    # y optimizar el acceso por posición frente a diccionarios.
    with open(original, MODO_LECTURA, newline="", encoding=CODIFICACION) as archivo:
        lector = csv.DictReader(archivo, delimiter=delimitador)
        columnas = lector.fieldnames or []
        # Asegura que 'columnas' siempre sea una lista, incluso si el archivo está vacío

        contadores = Counter()
        total_filas = 0

        for fila in lector:
            total_filas += 1
            for columna, valor in fila.items():
                if valor == "":
                    contadores[columna] += 1

        # Ahora usamos la variable 'columnas' que es segura
        return {col: round((contadores[col] / total_filas) * 100, 2)
                    if total_filas > 0 else 0.0 for col in columnas}


# Punto G
def registros_diferentes (original: Path, nombre_columna: str, delimitador = DELIMITADOR_TAB)-> int:
    """
    Cuenta la cantidad de valores diferentes en una columna.
    
    Args:
        original: ruta al archivo del dataset.
        nombre_columna: nombre de la columna a analizar.
        delimitador: caracter separador de campos (por defecto TAB).
    
    Returns:
        Cantidad de valores únicos en la columna.
    """
    with open(original, MODO_LECTURA, newline="", encoding=CODIFICACION) as archivo:
        lector = csv.DictReader(archivo, delimiter=delimitador)
        campos = set()
        for fila in lector:
            if nombre_columna in fila:
                campos.add(fila[nombre_columna])
        return len(campos)



# Punto H
def frecuencia_valores (original: Path, nombre_columna: str, delimitador = DELIMITADOR_TAB)-> dict:
    """
    Calcula la frecuencia de cada valor en una columna.

    Args:
        original: ruta al archivo del dataset.
        nombre_columna: nombre de la columna a analizar.
        delimitador: caracter separador de campos (por defecto TAB).

    Returns:
        Diccionario {valor: frecuencia} para cada valor en la columna.
    """
    with open(original, MODO_LECTURA, newline="", encoding=CODIFICACION) as archivo:
        lector = csv.DictReader(archivo, delimiter=delimitador)
        # Se utiliza 'Counter' en lugar de un bucle for con diccionarios estándar
        # para mejorar la legibilidad y eficiencia. Counter optimiza el proceso
        # de conteo internamente y maneja automáticamente la creación de llaves
        #  y la actualización de sus conteos.
        conteo = Counter(fila[nombre_columna] for fila in lector if nombre_columna in fila)
        return dict(conteo)


# Punto I
def analizar_columnas(original: Path, columna: str, tipo: str, delimitador: str = DELIMITADOR_TAB):
    """
    Analiza una columna según su tipo y retorna estadísticas.

    Args:
        original: ruta al archivo del dataset.
        columna: nombre de la columna a analizar.
        tipo: tipo de análisis ('numeric', 'coordinate', 'text').
        delimitador: caracter separador de campos (por defecto TAB).

    Returns:
        - numeric: (min, max, promedio)
        - coordinate: (min, max)
        - text: (min_len, max_len)
    """
    valores = []
    with open(original, MODO_LECTURA, newline='', encoding=CODIFICACION) as dataset:
        lector = csv.DictReader(dataset, delimiter=delimitador)
        if columna not in (lector.fieldnames or []):
            print(f"ERROR: columna '{columna}' no existe en el dataset")
            return None
        for fila in lector:
            if fila.get(columna, '') != '':
                valores.append(fila[columna])
    if not valores:
        return None

    if tipo == 'numeric':
        numeros = [float(v) for v in valores]
        return min(numeros), max(numeros), sum(numeros) / len(numeros)
    elif tipo == 'coordinate':
        numeros = [float(v) for v in valores]
        return min(numeros), max(numeros)
    elif tipo == 'text':
        largos = [len(v) for v in valores]
        return min(largos), max(largos)



# Punto J
def columnas_totalmente_vacias(original, delimitador=DELIMITADOR_TAB):
    """Retorna columnas con 100% de valores nulos."""
    vacios = registros_vacios(original, delimitador)
    return [col for col, pct in vacios.items() if pct == 100]


# TEST
if __name__ == "__main__":
    IADIZA = Path("..") / "datasets" / "IADIZA" / "occurrence.txt"
    INATURALIST = Path('..')/"datasets"/"iNaturalist"/"observations.csv"
    XENO_CANTO = Path('..')/"datasets"/"Xeno-canto"/"Occurrence.txt"
    for col, pct in registros_vacios(IADIZA).items():
        print(f"{col}: {pct}%")

    for nul in columnas_con_nulos(IADIZA):
        print(f"{nul}")
