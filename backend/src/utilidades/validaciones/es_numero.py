""" Funciones para validar coordenadas.
    - es_numero: devuelve true si el string representa un numero."""
def es_numero(valor: str) -> bool:
    """ devuelve true si el string representa un numero
    """
    if not valor:
        return False
    try:
        float(valor)
        return True
    except ValueError:
        return False
