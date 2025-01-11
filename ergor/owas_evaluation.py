def evaluate_owas(angles):
    """
    Evalúa los niveles de riesgo OWAS basados en los ángulos calculados.
    :param angles: Diccionario con los ángulos calculados.
    :return: Diccionario con puntajes OWAS y nivel de riesgo total.
    """
    back_score = 0
    arms_score = 0
    legs_score = 0

    # Evaluación de la espalda (back_score)
    if 0 <= angles["back"] <= 20:
        back_score = 1  # Riesgo bajo
    elif 21 <= angles["back"] <= 45:
        back_score = 2  # Riesgo moderado
    else:
        back_score = 3  # Riesgo alto

    # Evaluación de los brazos (arms_score)
    if 60 <= angles["arms"] <= 100:
        arms_score = 1  # Postura adecuada
    elif 40 <= angles["arms"] < 60 or 100 < angles["arms"] <= 120:
        arms_score = 2  # Ajuste necesario
    else:
        arms_score = 3  # Riesgo alto

    # Evaluación de las piernas (legs_score)
    if 0 <= angles["legs"] <= 30:
        legs_score = 1  # Postura estable
    elif 31 <= angles["legs"] <= 60:
        legs_score = 2  # Ajuste necesario
    else:
        legs_score = 3  # Riesgo alto

    # Cálculo del puntaje total
    total_score = back_score + arms_score + legs_score

    return {
        "back_score": back_score,
        "arms_score": arms_score,
        "legs_score": legs_score,
        "total_score": total_score,
        "risk_level": "Bajo" if total_score <= 3 else "Moderado" if total_score <= 6 else "Alto"
    }
    