"""Valida un registro antes de insertarlo."""
from ejercicio_3 import(
    fechas_invalidas, validar_country_code,
    validar_uncertainty 

)

from utilidades.validaciones import coordenadas_validas

def validar(registro: dict):
    """
      -Valida un registro con las validaciones del ej 3.
      -Devuelve una tupla (valido, errores): un bool que indica
       si cumple las condiciones y la lista de errores.
    """
    errores = []

    lat = registro.get('decimalLatitude', registro.get('latitudeDecimal', ""))
    lon = registro.get('decimalLongitude', registro.get('longitudeDecimal', ""))

    if not coordenadas_validas(lat,lon):
        errores.append("Coordenadas invalidas")

    fecha = registro.get('eventDate', "")
    if fecha != "":
        estado = fechas_invalidas(fecha)
        if estado != 'Valida':
            errores.append(f"fecha {estado}")

    codigo = registro.get('countryCode', "")
    if codigo != "" and not validar_country_code(codigo):
        errores.append("countryCode invalido")

    incertidumbre_val = registro.get('coordinateUncertaintyInMeters', "")
    if incertidumbre_val != "" and not validar_uncertainty(incertidumbre_val):
        errores.append("coordinateUncertaintyInMeters invalida")

    return len(errores) == 0, errores
