def evaluate_owas(angles, load_weight):
    """
    Evalúa las posturas corporales utilizando el método OWAS.
    :param angles: Diccionario con ángulos corporales promedio.
    :param load_weight: Peso de la carga manejada (en kg).
    :return: Diccionario con categorías OWAS para espalda, brazos, piernas y carga.
    """
    back_category = 0
    arms_category = 0
    legs_category = 0
    load_category = 0

    # Clasificación de espalda
    if angles["back"] <= 20:
        back_category = 1  # Postura neutra
    elif 20 < angles["back"] <= 45:
        back_category = 2  # Inclinación moderada
    else:
        back_category = 3  # Flexión excesiva

    # Clasificación de brazos
    if angles["arms"] <= 45:
        arms_category = 1  # Postura neutra
    elif 45 < angles["arms"] <= 90:
        arms_category = 2  # Elevación moderada
    else:
        arms_category = 3  # Elevación extrema

    # Clasificación de piernas
    if angles["legs"] <= 45:
        legs_category = 1  # Postura neutra
    elif 45 < angles["legs"] <= 90:
        legs_category = 2  # Inclinación o flexión moderada
    else:
        legs_category = 3  # Flexión extrema

    # Clasificación de carga
    if load_weight <= 10:
        load_category = 1  # Peso ligero
    elif 10 < load_weight <= 20:
        load_category = 2  # Peso moderado
    else:
        load_category = 3  # Peso pesado

    # Calcular categoría de acción OWAS
    action_category = back_category + arms_category + legs_category + load_category

    return {
        "back_category": back_category,
        "arms_category": arms_category,
        "legs_category": legs_category,
        "load_category": load_category,
        "action_category": action_category
    }
