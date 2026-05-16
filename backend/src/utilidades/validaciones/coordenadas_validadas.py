""" Funciones para validar coordenadas.
    - detectar_coordenadas_invalidas: detecta registros con coordenadas fuera 
        del rango valido global.
    - coordenadas_validas: valida que las coordenadas esten en rango y sean convertibles a numero.
    - es_numero: devuelve true si el string representa un numero."""

from utilidades.validaciones.es_numero import es_numero

def coordenadas_validas(lat: str, lon: str):
    """ Valida las coordenadas en rango.
         -es invalido si la latitud no esta en [-90:90]
         -es invalido si la longitus no esta en [-180:180]
         -algun valor que no pueda convertirse a numero
    """
    lat = lat.strip() if lat else ''
    lon = lon.strip() if lon else ''
    if not es_numero(lat) or not es_numero(lon):
        return False
    lat_numero = float(lat)
    lon_numero = float(lon)
    if not -90 <= lat_numero <= 90:
        return False
    if not -180 <= lon_numero <= 180:
        return False
    return True
