"""Pide datos al usuario por teclado."""

# Campos que se validan en ejercicio_3 - solo estos son importantes
# Tuple: (nombre del campo, ayuda de qué ingresar)
CAMPOS_IMPORTANTES = [
    ('decimalLatitude', 'número entre -90 y 90'),
    ('decimalLongitude', 'número entre -180 y 180'),
    ('eventDate', 'fecha formato YYYY-MM-DD'),
    ('countryCode', 'código ISO 2 letras (AR, BR, CL...)'),
    ('coordinateUncertaintyInMeters', 'número positivo en metros'),
    ('scientificName', 'nombre científico de la especie'),
    ('stateProvince', 'provincia/estado'),
    ('county', 'departamento/county'),
    ('locality', 'localidad específica'),
]


def pedir_datos_por_columna(
    columnas: list,
    campo_id: str | None = None,
    valor_id: str | None = None
) -> dict:
    """
    Pide datos al usuario SOLO para los campos importantes del dataset.
    El resto se completa automáticamente con vacío.
    
    Parametros
    ----------
    columnas : list
        Lista de nombres de columnas del dataset.
    campo_id : str, opcional
        Nombre del campo de ID (se omite en la entrada).
    valor_id : str, opcional
        Valor del ID calculado automáticamente.
    
    Retornos
    -------
    dict
        Diccionario con {columna: valor}.
    """
    registro = {}
    # 0. Asignar ID automatico si existe (aunque no este en CAMPOS_IMPORTANTES)
    if campo_id and valor_id is not None:
        registro[campo_id] = valor_id
        if campo_id not in [c for c, _ in CAMPOS_IMPORTANTES]:
            print(f"{campo_id}: {valor_id} (asignado automaticamente)")
    # 1. Solo pedir campos importantes que existen en este dataset
    for nombre_campo, ayuda in CAMPOS_IMPORTANTES:
        if nombre_campo in columnas and nombre_campo != campo_id:
            valor = input(f"Ingrese {nombre_campo} ({ayuda}): ")
            registro[nombre_campo] = valor
    # 2. Completar el resto con vacío (los ~90+ campos no pedidos)
    for col in columnas:
        if col not in registro:
            registro[col] = ""
    
    return registro