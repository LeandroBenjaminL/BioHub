""" Ejercicio 3 - Validación de datos
    En este ejercicio se implementan funciones para validar la calidad 
    de los datos en un dataset."""
import csv
from pathlib import Path
from datetime import datetime
from collections import Counter
from constantes import (CODIFICACION, DELIMITADOR_TAB, MODO_LECTURA, LAT_MIN_SUDAMERICA,
                         LAT_MAX_SUDAMERICA, LON_MIN_SUDAMERICA, LON_MAX_SUDAMERICA,MAX)

from codigos_paises import CODIGOS_PAISES
from utilidades.validaciones import coordenadas_validas, es_numero, detectar_campo_id

# PUNTO 3A

def detectar_coordenadas_invalidas(original: Path, delimitador=DELIMITADOR_TAB):
    """Detecta registros con coordenadas fuera del rango valido global.

    Valida que:
        - decimalLatitude este en [-90, 90]
        - decimalLongitude este en [-180, 180]
        - los valores sean convertibles a numero

    Parametros:
        original: ruta al archivo del dataset.
        delimitador: caracter separador de campos (por defecto TAB).

    Devuelve:
        tuple: (cantidad_invalidos, lista_registros_invalidos)
    """
    with open(original, MODO_LECTURA, newline='', encoding=CODIFICACION) as archivo:
        lector = csv.DictReader(archivo, delimiter=delimitador)
        columnas = lector.fieldnames or []

        if 'decimalLatitude' in columnas:
            col_lat = 'decimalLatitude'
        else:
            col_lat = 'latitudeDecimal'

        if 'decimalLongitude' in columnas:
            col_lon = 'decimalLongitude'
        else:
            col_lon = 'longitudeDecimal'

        cantidad_invalidos = 0
        registros_invalidos = []

        for registro in lector:
            lat = registro.get(col_lat, '')
            lon = registro.get(col_lon, '')
            if not coordenadas_validas(lat, lon):
                cantidad_invalidos += 1
                registros_invalidos.append(registro)

    return cantidad_invalidos, registros_invalidos


# punto 3b
def ambas_coordenadas(latitud: str, longitud: str) -> bool:
    """Entran dos strings, latitud y longitud y chequea que este uno, pero no el otro"""
    lat = latitud.strip()
    lon = longitud.strip()
    if not lat and es_numero(lon):
        return True
    elif es_numero(lat) and not lon:
        return True
    return False


def latitud_longitud(original: Path, delimitador=DELIMITADOR_TAB) -> int:
    """ Imprime y retorna la cantidad de registros incorrectos donde
      existe una coordenada pero no la otra"""

    with open(original, MODO_LECTURA, newline='', encoding=CODIFICACION) as dataset:
        lector = csv.DictReader(dataset, delimiter=delimitador)
        fieldnames = lector.fieldnames or []
        if 'decimalLatitude' in fieldnames:
            columna_lat = 'decimalLatitude'
        else:
            columna_lat = 'latitudeDecimal'

        if 'decimalLongitude' in fieldnames:
            columna_lon = 'decimalLongitude'
        else:
            columna_lon = 'longitudeDecimal'

        contador_falta1 = 0
        for linea in lector:
            if ambas_coordenadas(linea[columna_lat], linea[columna_lon]):
                contador_falta1 += 1
    return contador_falta1


# Punto 3c
def fechas_invalidas(elemento: str) -> str:
    """Retorna si la fecha es valida, invalida, posterior o no es una fecha
        Argumentos = string
        Retorna = string "Valida", "Invalida", "Posterior" o "No fecha"

    """
    hoy = datetime.now()
    if not elemento:
        return "No fecha"
    fecha = elemento.split('-')
    if len(fecha)>=3:
        if len(fecha[0]) == 4 and es_numero(fecha[1]) and es_numero(fecha[2][:2]):
            try:
                fecha = datetime.strptime(elemento[:10], '%Y-%m-%d')
                if fecha > hoy:
                    return "Posterior"
                else:
                    return "Valida"
            except ValueError:
                return "Invalida"
        else:
            return "No fecha"


# Punto 3D
def registros_duplicados(original: Path, delimitador=DELIMITADOR_TAB):
    """ Detecta posibles registros duplicados segun su ID 
        Parametros:
            original: ruta al archivo del dataset.
            delimitador: caracter separador de campos (por defecto TAB).

        Devuelve:
            Entero con cantidad de duplicados, lista de ids repetidos
    """

    with open(original, MODO_LECTURA, newline='', encoding=CODIFICACION) as dataset:
        lector = csv.DictReader(dataset, delimiter=delimitador)
        header = [col.strip() for col in (lector.fieldnames or [])]
        
        columna_id = detectar_campo_id(header)
        if columna_id is None:
            print(f"ERROR: no se detecto columna de ID en {original}")
            return 0, []

        conteo = Counter()
        for fila in lector:
            fila_limpia = {k.strip(): v for k, v in fila.items() if k is not None}
            conteo[fila_limpia.get(columna_id, '')] += 1

        repetidos = {id: cantidad for id, cantidad in conteo.items() 
                     if id and cantidad > 1}
        total_duplicados = sum(cant - 1 for cant in repetidos.values())

    return total_duplicados, list(repetidos.keys())

# Punto 3E
def validar_country_code(codigo: str) -> bool:
    """ Verifica que el campo countryCode sea valido segun el estandar ISO 3166-1 alpha-2 
        Parametros:
            codigo: countryCode a verificar

        Devuelve:
            Boolean true para valido, false para invalido
    """
    validos = CODIGOS_PAISES
    return codigo in validos

#PUNTO 3F
def validar_uncertainty(valor: str):
    """Validar coordinateUncertaintyInMeters.
       - es invalido si el valor no es numero.
       - es invalido si es negativo.
       - es invalido si es > 100. 
    """
    if not es_numero(valor):
        return False
    numero = float(valor)
    if numero < 0:
        return False
    if numero > MAX:
        return False
    return True

# PUNTO 3G
def resumen_calidad(original: Path, delimitador=DELIMITADOR_TAB):
    """Genera un resumen de calidad del dataset."""
    with open(original, MODO_LECTURA, newline='', encoding=CODIFICACION) as archivo:
        lector = csv.DictReader(archivo, delimiter=delimitador)
        columnas = lector.fieldnames or []

        # deteccion de nombre dependiendo el dataset
        if 'decimalLatitude' in columnas:
            columna_lat = 'decimalLatitude'
        else:
            columna_lat = 'latitudeDecimal'
        if 'decimalLongitude' in columnas:
            columna_lon = 'decimalLongitude'
        else:
            columna_lon = 'longitudeDecimal'

        # agarro los datos taxo del dataset
        taxo = [c for c in ['kingdom', 'phylum', 'class', 'order', 'family', 'genus']
                 if c in columnas]

        total = 0
        coords_invalidas = 0
        fechas_malas = 0
        taxonomia_incompleta = 0

        for fila in lector:
            total += 1
            if not validar_latitud(fila.get(columna_lat, '')) or not validar_longitud(fila.get(columna_lon, '')):
                coords_invalidas += 1
            if fechas_invalidas(fila.get('eventDate', '')) in ('Invalida', 'Posterior'):
                fechas_malas += 1
            # si encuentro un taxo vacio, marco la fila como incompleta y salgo
            for campo in taxo:
                if not fila.get(campo, '').strip():
                    taxonomia_incompleta += 1
                    break

    duplicados, _ = registros_duplicados(original, delimitador)

    resumen = {
        'total': total,
        'coordenadas_invalidas': coords_invalidas,
        'fechas_invalidas': fechas_malas,
        'duplicados': duplicados,
        'taxonomia_incompleta': taxonomia_incompleta,
    }

    print(f"Total registros: {total}")
    print(f"Coordenadas invalidas: {coords_invalidas}")
    print(f"Fechas invalidas: {fechas_malas}")
    print(f"Duplicados: {duplicados}")
    print(f"Info taxonomica incompleta: {taxonomia_incompleta}")

    return resumen


# PUNTO 3I
def validar_latitud(lat):
    """Corre todas las validaciones de latitud."""
    lon_falsa = "-60"
    return coordenadas_validas(lat, lon_falsa) and validar_coordenadas_sudamerica(lat, lon_falsa)


def validar_longitud(lon):
    """Corre todas las validaciones de longitud."""
    lat_falsa = "0"
    return coordenadas_validas(lat_falsa, lon) and validar_coordenadas_sudamerica(lat_falsa, lon)


# PUNTO 3H
def validar_coordenadas_sudamerica(lat: str, lon: str):
    """Valida si las coordenadas estan dentro de las cotas de America del Sur.
       es invalido si la latitus no esta en el rango[-56.0:13.0]
       es invalido si la longitud no esta en el rango[-82.0:-31.0]
    """
    if not es_numero(lat) or not es_numero(lon):
        return False
    lat_numero = float(lat)
    lon_numero = float(lon)
    if not LAT_MIN_SUDAMERICA <= lat_numero <= LAT_MAX_SUDAMERICA:
        return False
    if not LON_MIN_SUDAMERICA <= lon_numero <= LON_MAX_SUDAMERICA:
        return False
    return True
