"""Excepciones custom del proyecto."""


class ErrorDataset(Exception):
    """Error general relacionado con datasets."""



class ErrorColumnas(ErrorDataset):
    """Error al obtener o procesar columnas del dataset."""



class ErrorValidacion(ErrorDataset):
    """Error de validación de datos."""
