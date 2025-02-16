import numpy as np

def evaluate_ROSA(angles, usage_times=None):
    """
    Calcula puntajes detallados de ROSA basados en los ángulos proporcionados y tiempos de uso.
    :param angles: Diccionario con los ángulos calculados.
    :param usage_times: Diccionario con los tiempos de uso de cada elemento.
    :return: Diccionario con puntajes ROSA y puntaje total.
    """
    
    # Valores por defecto para el tiempo de uso (parametrizados)
    if usage_times is None:
        usage_times = {
            "chair": 0,  # 0 puntos (entre 1 y 4 horas en total o 30 minutos ininterrumpidos)
            "monitor": 0,
            "keyboard": 0,
            "phone": 0,
            "mouse": 0
        }
    
    # Inicialización de puntuaciones
    chair_score = 0
    monitor_score = 0
    keyboard_score = 0
    phone_score = 0
    mouse_score = 0
    suma_profundidad = 0
    suma_altura = 0
    suma_reposabrazos = 0
    suma_respaldo = 0

    # Evaluación de la altura del asiento (Tabla 2)
    if angles["knee"] < 85:
        suma_altura += 2  # Asiento muy bajo, ángulo de rodilla < 90º
        if angles.get("feet_contact", 1) == 0:  # Pies no tienen contacto con el suelo
            suma_altura += 1
    elif angles["knee"] > 95:
        suma_altura += 2  # Asiento muy alto, ángulo de rodilla > 90º
    else:
        suma_altura += 1  # Ángulo de rodilla aprox. 90º

    # Incrementos adicionales para la altura del asiento
    if angles.get("leg_space", 0) == 0:  # Espacio insuficiente para las piernas
        suma_altura += 1
    if angles.get("seat_height_adjustable", 0) == 0:  # Altura no regulable
        suma_altura += 1

    # Evaluación de la profundidad del asiento (Tabla 3)
    if angles.get("seat_depth", 8) < 8:
        suma_profundidad += 2  # Asiento muy largo
    elif angles.get("seat_depth", 8) > 8:
        suma_profundidad += 2  # Asiento muy corto
    else:
        suma_profundidad += 1  # Espacio adecuado

    # Incremento adicional para la profundidad del asiento
    if angles.get("seat_depth_adjustable", 0) == 0:  # Profundidad no regulable
        suma_profundidad += 1

    # Evaluación de los reposabrazos (Tabla 4)
    if angles["elbow"] < 85 or angles["elbow"] > 95:
        chair_score += 2  # Reposabrazos demasiado altos o bajos
    else:
        chair_score += 1  # Codos bien apoyados

    # Incrementos adicionales para los reposabrazos
    if angles.get("armrest_separation", 0) == 1:  # Reposabrazos demasiado separados
        suma_reposabrazos += 1
    if angles.get("armrest_surface", 0) == 1:  # Superficie dura o dañada
        suma_reposabrazos += 1
    if angles.get("armrest_adjustable", 0) == 0:  # Reposabrazos no ajustables
        suma_reposabrazos += 1

    # Evaluación del respaldo (Tabla 5)
    if angles["back"] < 95 or angles["back"] > 110:
        suma_respaldo += 2  # Respaldo no reclinado adecuadamente
    else:
        suma_respaldo += 1  # Respaldo reclinado adecuadamente

    # Incrementos adicionales para el respaldo
    if angles.get("work_surface_height", 0) == 1:  # Superficie de trabajo demasiado alta
        suma_respaldo += 1
    if angles.get("backrest_adjustable", 0) == 0:  # Respaldo no ajustable
        suma_respaldo += 1

    # Matriz de puntuación de la silla (Tabla A)
    tabla_A = np.array([
        [2, 2, 3, 4, 5, 6, 7, 8],
        [2, 2, 3, 4, 5, 6, 7, 8],
        [3, 3, 3, 4, 5, 6, 7, 8],
        [4, 4, 4, 4, 5, 6, 7, 8],
        [5, 5, 5, 5, 6, 7, 8, 9],
        [6, 6, 6, 7, 7, 8, 8, 9],
        [7, 7, 7, 8, 8, 9, 9, 9]
    ])
    suma_altura_profundidad = suma_altura + suma_profundidad  # Suponiendo que chair_score ya es la suma de altura y profundidad
    suma_reposabrazos_respaldo = suma_reposabrazos + suma_respaldo  # Suponiendo que chair_score ya es la suma de reposabrazos y respaldo
    chair_score = tabla_A[min(suma_altura_profundidad - 2, 6)][min(suma_reposabrazos_respaldo - 2, 7)]
    
    # Ajuste por tiempo de uso de la silla (Tabla 7)
    chair_score += usage_times["chair"]

    # Evaluación de la pantalla (Tabla 8)
    if angles["monitor_distance"] < 45:
        monitor_score += 2  # Pantalla muy baja
    elif angles["monitor_distance"] > 75:
        monitor_score += 3  # Pantalla demasiado alta
    else:
        monitor_score += 1  # Distancia adecuada

    # Incrementos adicionales para la pantalla
    if angles.get("monitor_lateral_deviation", 0) == 1:  # Pantalla desviada lateralmente
        monitor_score += 1
    if angles.get("document_holder", 0) == 0:  # No hay atril para documentos
        monitor_score += 1
    if angles.get("monitor_glare", 0) == 1:  # Brillos o reflejos en la pantalla
        monitor_score += 1
    if angles.get("monitor_too_far", 0) == 1:  # Pantalla muy lejos
        monitor_score += 1

    # Ajuste por tiempo de uso del monitor (Tabla 7)
    monitor_score += usage_times["monitor"]

    # Evaluación del teléfono (Tabla 9)
    if angles["phone_distance"] > 30:
        phone_score += 2  # Teléfono lejos
    else:
        phone_score += 1  # Teléfono cerca

    # Incrementos adicionales para el teléfono
    if angles.get("phone_shoulder", 0) == 1:  # Teléfono sujetado entre cuello y hombro
        phone_score += 2
    if angles.get("phone_hands_free", 0) == 0:  # Teléfono no tiene función manos libres
        phone_score += 1

    # Ajuste por tiempo de uso del teléfono (Tabla 7)
    phone_score += usage_times["phone"]

    # Evaluación del teclado (Tabla 12)
    if angles["wrist"] > 15:
        keyboard_score += 2  # Muñecas extendidas más de 15º
    else:
        keyboard_score += 1  # Muñecas rectas

    # Incrementos adicionales para el teclado
    if angles.get("wrist_deviation", 0) == 1:  # Muñecas desviadas lateralmente
        keyboard_score += 1
    if angles.get("keyboard_height", 0) == 1:  # Teclado demasiado alto
        keyboard_score += 1
    if angles.get("keyboard_adjustable", 0) == 0:  # Teclado no ajustable
        keyboard_score += 1

    # Ajuste por tiempo de uso del teclado (Tabla 7)
    keyboard_score += usage_times["keyboard"]

    # Evaluación del mouse (Tabla 11)
    if angles.get("mouse_alignment", 0) == 0:  # Mouse no alineado con el hombro
        mouse_score += 2
    else:
        mouse_score += 1  # Mouse alineado con el hombro

    # Incrementos adicionales para el mouse
    if angles.get("mouse_size", 0) == 1:  # Mouse muy pequeño
        mouse_score += 1
    if angles.get("mouse_surface", 0) == 1:  # Superficie dura o puntos de presión
        mouse_score += 1
    if angles.get("mouse_keyboard_height_diff", 0) == 1:  # Mouse y teclado a diferentes alturas
        mouse_score += 2

    # Ajuste por tiempo de uso del mouse (Tabla 7)
    mouse_score += usage_times["mouse"]

    # Matriz de puntuación de pantalla y teléfono (Tabla B)
    tabla_B = np.array([
        [1, 1, 1, 2, 3, 4, 5, 6],
        [1, 1, 2, 2, 3, 4, 5, 6],
        [1, 2, 2, 3, 3, 4, 6, 7],
        [2, 2, 3, 3, 4, 5, 6, 8],
        [3, 3, 4, 4, 5, 6, 7, 8],
        [4, 4, 5, 5, 6, 7, 8, 9],
        [5, 5, 6, 7, 8, 8, 9, 9]
    ])
    monitor_phone_score = tabla_B[min(monitor_score, 6)][min(phone_score, 7)]

    # Matriz de puntuación de teclado y mouse (Tabla C)
    tabla_C = np.array([
        [1, 1, 1, 2, 3, 4, 5, 6],
        [1, 1, 2, 3, 4, 5, 6, 7],
        [1, 2, 2, 3, 4, 5, 6, 7],
        [2, 3, 3, 3, 5, 6, 7, 8],
        [3, 4, 4, 5, 5, 6, 7, 8],
        [4, 5, 5, 6, 6, 7, 8, 9],
        [5, 6, 6, 7, 7, 8, 8, 9],
        [6, 7, 7, 8, 8, 9, 9, 9]
    ])
    keyboard_mouse_score = tabla_C[min(keyboard_score, 7)][min(mouse_score, 7)]

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
    peripherals_score = tabla_D[min(monitor_phone_score, 8)][min(keyboard_mouse_score, 8)]

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
        "mouse_score": mouse_score,
        "total_score": total_score
    }