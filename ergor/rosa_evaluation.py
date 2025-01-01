from ergor import db
from models import User,RosaScore
from rosa_evaluation import evaluate_rosa

def evaluate_rosa(angles):
    """
    Calcula puntajes detallados de ROSA basados en los ángulos proporcionados.
    :param angles: Diccionario con los ángulos calculados.
    :return: Diccionario con puntajes ROSA y puntaje total.
    """
    chair_score = 0
    monitor_score = 0
    keyboard_score = 0
    phone_score = 0

    # Evaluación de silla (chair_score)
    if 90 <= angles["hip"] <= 110:
        chair_score += 1  # Postura adecuada
    elif 70 <= angles["hip"] < 90 or 110 < angles["hip"] <= 130:
        chair_score += 2  # Ajuste necesario
    else:
        chair_score += 3  # Revisión urgente

    # Evaluación del monitor (monitor_score)
    if 0 <= angles["shoulder"] <= 20:
        monitor_score += 1  # Altura adecuada
    elif 20 < angles["shoulder"] <= 40:
        monitor_score += 2  # Requiere ajuste
    else:
        monitor_score += 3  # Riesgo alto

    # Evaluación del teclado/ratón (keyboard_score)
    if 70 <= angles["elbow"] <= 100 and -10 <= angles["wrist"] <= 10:
        keyboard_score += 1  # Postura adecuada
    elif 60 <= angles["elbow"] < 70 or 100 < angles["elbow"] <= 120:
        keyboard_score += 2  # Ajuste necesario
    else:
        keyboard_score += 3  # Revisión urgente

    # Evaluación del teléfono (phone_score)
    # Este puntaje podría ser un parámetro fijo o evaluado según tiempo de uso
    phone_score = 1  # Ejemplo: uso moderado (ajustar según datos reales)

    # Cálculo del puntaje total
    total_score = chair_score + monitor_score + keyboard_score + phone_score
    
    # Guardar en la base de datos
    rosa_score = RosaScore(
        user_id=user_id,
        chair_score=chair_score,
        monitor_score=monitor_score,
        phone_score=phone_score,
        keyboard_score=keyboard_score,
        total_score=total_score,
        evaluation_date=datetime.now()
    )
    db.session.add(rosa_score)
    db.session.commit()

    return {
        "chair_score": chair_score,
        "monitor_score": monitor_score,
        "keyboard_score": keyboard_score,
        "phone_score": phone_score,
        "total_score": total_score
    }