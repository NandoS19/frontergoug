import numpy as np

def evaluate_ROSA(angles, usage_times=None):
    """
    Calcula puntajes detallados de ROSA basados en los ángulos proporcionados y tiempos de uso.
    :param angles: Diccionario con los ángulos calculados.
    :param usage_times: Diccionario con los tiempos de uso de cada elemento.
    :return: Diccionario con puntajes ROSA y puntaje total.
    """
    
    if usage_times is None:
        usage_times = {
            "chair": -1,
            "monitor": -1,
            "keyboard": -1,
            "phone": -1
        }
    
    chair_score = 0
    monitor_score = 0
    keyboard_score = 0
    phone_score = 0

    # Evaluación de la altura del asiento (Tabla 2)
    if 85 <= angles["knee"] <= 95:
        chair_score += 1
    elif angles["knee"] < 85 or angles["knee"] > 95:
        chair_score += 2
    if angles["knee"] < 85:
        chair_score += 3

    # Evaluación de la profundidad del asiento (Tabla 3)
    if 8 <= angles["seat_depth"] <= 12:
        chair_score += 1
    else:
        chair_score += 2

    # Evaluación de los reposabrazos (Tabla 4)
    if 85 <= angles["elbow"] <= 95:
        chair_score += 1
    else:
        chair_score += 2

    # Evaluación del respaldo (Tabla 5)
    if 95 <= angles["back"] <= 110:
        chair_score += 1
    else:
        chair_score += 2
    
    # Ajuste por tiempo de uso (Tabla 7)
    chair_score += usage_times["chair"]

    # Matriz de puntuación de la silla (Tabla A)
    tabla_A = np.array([
        [2, 3, 4, 5, 6, 7, 8, 9],
        [2, 3, 4, 5, 6, 7, 8, 9],
        [3, 3, 4, 5, 6, 7, 8, 9],
        [4, 4, 4, 5, 6, 7, 8, 9],
        [5, 5, 5, 6, 7, 8, 9, 9],
        [6, 6, 7, 7, 8, 8, 9, 9],
        [7, 7, 8, 8, 9, 9, 9, 9]
    ])
    chair_score = tabla_A[min(chair_score, 6)][min(chair_score, 7)]

    # Evaluación de la pantalla (Tabla 8)
    if 45 <= angles["monitor_distance"] <= 75:
        monitor_score += 1
    elif angles["monitor_distance"] < 45:
        monitor_score += 2
    else:
        monitor_score += 3
    monitor_score += usage_times["monitor"]

    # Evaluación del teléfono (Tabla 9)
    if angles["phone_distance"] <= 30:
        phone_score += 1
    else:
        phone_score += 2
    phone_score += usage_times["phone"]

    # Evaluación del teclado (Tabla 12)
    if 0 <= angles["wrist"] <= 15:
        keyboard_score += 1
    else:
        keyboard_score += 2
    keyboard_score += usage_times["keyboard"]

    # Matriz de puntuación de pantalla y periféricos (Tabla D)
    tabla_D = np.array([
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [2, 2, 3, 4, 5, 6, 7, 8, 9],
        [3, 3, 3, 4, 5, 6, 7, 8, 9],
        [4, 4, 4, 4, 5, 6, 7, 8, 9],
        [5, 5, 5, 5, 5, 6, 7, 8, 9],
        [6, 6, 6, 6, 6, 6, 7, 8, 9],
        [7, 7, 7, 7, 7, 7, 7, 8, 9],
        [8, 8, 8, 8, 8, 8, 8, 8, 9],
        [9, 9, 9, 9, 9, 9, 9, 9, 9]
    ])
    peripherals_score = tabla_D[min(monitor_score, 8)][min(phone_score + keyboard_score, 8)]

    # Matriz de puntuación final ROSA (Tabla E)
    tabla_E = np.array([
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [2, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [3, 3, 3, 4, 5, 6, 7, 8, 9, 10],
        [4, 4, 4, 4, 5, 6, 7, 8, 9, 10],
        [5, 5, 5, 5, 5, 6, 7, 8, 9, 10],
        [6, 6, 6, 6, 6, 6, 7, 8, 9, 10],
        [7, 7, 7, 7, 7, 7, 7, 8, 9, 10],
        [8, 8, 8, 8, 8, 8, 8, 8, 9, 10],
        [9, 9, 9, 9, 9, 9, 9, 9, 9, 10],
        [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    ])
    total_score = tabla_E[min(chair_score, 9)][min(peripherals_score, 9)]

    return {
        "chair_score": chair_score,
        "monitor_score": monitor_score,
        "keyboard_score": keyboard_score,
        "phone_score": phone_score,
        "total_score": total_score
    }


# def evaluate_rosa(angles):
#     """
#     Calcula puntajes detallados de ROSA basados en los ángulos proporcionados.
#     :param angles: Diccionario con los ángulos calculados.
#     :return: Diccionario con puntajes ROSA y puntaje total.
#     """
#     chair_score = 0
#     monitor_score = 0
#     keyboard_score = 0
#     phone_score = 0

#     # Evaluación de silla (chair_score)
#     if 90 <= angles["hip"] <= 110:
#         chair_score += 1  # Postura adecuada
#     elif 70 <= angles["hip"] < 90 or 110 < angles["hip"] <= 130:
#         chair_score += 2  # Ajuste necesario
#     else:
#         chair_score += 3  # Revisión urgente

#     # Evaluación del monitor (monitor_score)
#     if 0 <= angles["shoulder"] <= 20:
#         monitor_score += 1  # Altura adecuada
#     elif 20 < angles["shoulder"] <= 40:
#         monitor_score += 2  # Requiere ajuste
#     else:
#         monitor_score += 3  # Riesgo alto

#     # Evaluación del teclado/ratón (keyboard_score)
#     if 70 <= angles["elbow"] <= 100:
#         keyboard_score += 1  # Postura adecuada
#     elif 60 <= angles["elbow"] < 70 or 100 < angles["elbow"] <= 120:
#         keyboard_score += 2  # Ajuste necesario
#     else:
#         keyboard_score += 3  # Revisión urgente

#     # Evaluación del teléfono (phone_score)
#     phone_score = 1  # Puntaje fijo para este ejemplo

#     # Cálculo del puntaje total
#     total_score = chair_score + monitor_score + keyboard_score + phone_score

#     return {
#         "chair_score": chair_score,
#         "monitor_score": monitor_score,
#         "keyboard_score": keyboard_score,
#         "phone_score": phone_score,
#         "total_score": total_score
#     }

# def evaluate_Rosa(angles, usage_times=None):
#     """
#     Calcula puntajes detallados de ROSA basados en los ángulos proporcionados y tiempos de uso.
#     :param angles: Diccionario con los ángulos calculados.
#     :param usage_times: Diccionario con los tiempos de uso de cada elemento.
#     :return: Diccionario con puntajes ROSA y puntaje total.
#     """
    
#     if usage_times is None:
#         usage_times = {
#             "chair": -1,  # Por defecto, 1 hora de uso de la silla
#             "monitor": -1,  # Por defecto, 1 hora de uso del monitor
#             "keyboard": -1,  # Por defecto, 1 hora de uso del teclado
#             "phone": -1  # Por defecto, 1 hora de uso del teléfono
#         }
    
#     chair_score = 0
#     monitor_score = 0
#     keyboard_score = 0
#     phone_score = 0

#     # Evaluación de la altura del asiento
#     if 85 <= angles["knee"] <= 95:
#         chair_score += 1  # Rodillas flectadas 90 grados aproximadamente
#     elif angles["knee"] < 85 or angles["knee"] > 95:
#         chair_score += 2  # Asiento muy bajo o muy alto
#     if angles["knee"] < 85:
#         chair_score += 3  # Pies no tienen contacto con el suelo

#     # Evaluación de la profundidad del asiento
#     if 8 <= angles["seat_depth"] <= 12:
#         chair_score += 1  # Espacio adecuado entre asiento y rodillas
#     else:
#         chair_score += 2  # Asiento muy largo o muy corto

#     # Evaluación de los reposabrazos
#     if 85 <= angles["elbow"] <= 95:
#         chair_score += 1  # Codos bien apoyados y hombros relajados
#     else:
#         chair_score += 2  # Reposabrazos demasiado altos o bajos

#     # Evaluación del respaldo
#     if 95 <= angles["back"] <= 110:
#         chair_score += 1  # Respaldo reclinado adecuadamente
#     else:
#         chair_score += 2  # Sin apoyo lumbar o respaldo no adecuado

#     # Evaluación del monitor
#     if 45 <= angles["monitor_distance"] <= 75:
#         monitor_score += 1  # Distancia adecuada de la pantalla
#     elif angles["monitor_distance"] < 45:
#         monitor_score += 2  # Pantalla muy baja
#     else:
#         monitor_score += 3  # Pantalla demasiado alta

#     # Evaluación del teclado
#     if 0 <= angles["wrist"] <= 15:
#         keyboard_score += 1  # Muñecas rectas y hombros relajados
#     else:
#         keyboard_score += 2  # Muñecas extendidas más de 15 grados

#     # Evaluación del teléfono
#     if angles["phone_distance"] <= 30:
#         phone_score += 1  # Teléfono cerca y cuello en posición neutral
#     else:
#         phone_score += 2  # Teléfono lejos

#     # Ajuste por tiempo de uso
#     chair_score += usage_times["chair"]
#     monitor_score += usage_times["monitor"]
#     keyboard_score += usage_times["keyboard"]
#     phone_score += usage_times["phone"]

#     # Cálculo del puntaje total
#     total_score = chair_score + monitor_score + keyboard_score + phone_score

#     return {
#         "chair_score": chair_score,
#         "monitor_score": monitor_score,
#         "keyboard_score": keyboard_score,
#         "phone_score": phone_score,
#         "total_score": total_score
#     }
    
