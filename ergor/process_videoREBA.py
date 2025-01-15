import cv2
import mediapipe as mp
import numpy as np
import math

# Inicialización de Mediapipe para detección de puntos clave
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Función para obtener el código postural según el ángulo
def obtener_codigo_postural(angulo, parte_del_cuerpo):
    if parte_del_cuerpo == "cuello":
        if angulo < 30:
            return 1  # Ideal
        elif angulo < 60:
            return 2  # Aceptable
        else:
            return 3  # Peligroso
    elif parte_del_cuerpo == "espalda":
        if angulo < 45:
            return 1  # Ideal
        elif angulo < 90:
            return 2  # Aceptable
        else:
            return 3  # Peligroso
    elif parte_del_cuerpo == "piernas":
        if angulo < 40:
            return 1  # Ideal
        elif angulo < 80:
            return 2  # Aceptable
        else:
            return 3  # Peligroso
    elif parte_del_cuerpo == "brazos":
        if angulo < 60:
            return 1  # Ideal
        elif angulo < 120:
            return 2  # Aceptable
        else:
            return 3  # Peligroso
    elif parte_del_cuerpo == "antebrazos":
        if angulo < 45:
            return 1  # Ideal
        elif angulo < 90:
            return 2  # Aceptable
        else:
            return 3  # Peligroso
    elif parte_del_cuerpo == "muñeca":
        if angulo < 30:
            return 1  # Ideal
        elif angulo < 60:
            return 2  # Aceptable
        else:
            return 3  # Peligroso
    return 3  # Valor por defecto si la parte del cuerpo no coincide

    if angulo is None:
        return 1

# Función para calcular el ángulo entre tres puntos
def calculate_angle(landmarks, part):
    if part == "trunk":
        # Calculando el ángulo para el tronco (hombros, cadera)
        p1 = np.array([landmarks[11].x, landmarks[11].y])  # Hombro izquierdo
        p2 = np.array([landmarks[23].x, landmarks[23].y])  # Cadera izquierda
        p3 = np.array([landmarks[24].x, landmarks[24].y])  # Cadera derecha
        return np.degrees(np.arctan2(p3[1] - p2[1], p3[0] - p2[0]) - np.arctan2(p1[1] - p2[1], p1[0] - p2[0]))
    elif part == "neck":
        # Calculando el ángulo del cuello (ojos, nariz)
        p1 = np.array([landmarks[0].x, landmarks[0].y])  # Ojo izquierdo
        p2 = np.array([landmarks[1].x, landmarks[1].y])  # Nariz
        p3 = np.array([landmarks[2].x, landmarks[2].y])  # Ojo derecho
        return np.degrees(np.arctan2(p3[1] - p2[1], p3[0] - p2[0]) - np.arctan2(p1[1] - p2[1], p1[0] - p2[0]))
    elif part == "leg":
        # Calculando el ángulo de las piernas (cadera, rodilla, tobillo)
        p1 = np.array([landmarks[23].x, landmarks[23].y])  # Cadera izquierda
        p2 = np.array([landmarks[25].x, landmarks[25].y])  # Rodilla izquierda
        p3 = np.array([landmarks[27].x, landmarks[27].y])  # Tobillo izquierdo
        return np.degrees(np.arctan2(p3[1] - p2[1], p3[0] - p2[0]) - np.arctan2(p1[1] - p2[1], p1[0] - p2[0]))
    elif part == "upper_arm":
        # Calculando el ángulo de los brazos (hombro, codo, muñeca)
        p1 = np.array([landmarks[11].x, landmarks[11].y])  # Hombro izquierdo
        p2 = np.array([landmarks[13].x, landmarks[13].y])  # Codo izquierdo
        p3 = np.array([landmarks[15].x, landmarks[15].y])  # Muñeca izquierda
        return np.degrees(np.arctan2(p3[1] - p2[1], p3[0] - p2[0]) - np.arctan2(p1[1] - p2[1], p1[0] - p2[0]))
    elif part == "lower_arm":
        # Calculando el ángulo del antebrazo (codo, muñeca)
        p1 = np.array([landmarks[13].x, landmarks[13].y])  # Codo izquierdo
        p2 = np.array([landmarks[15].x, landmarks[15].y])  # Muñeca izquierda
        return np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))
    elif part == "wrist":
        # Calculando el ángulo de la muñeca (muñeca, dedos)
        p1 = np.array([landmarks[15].x, landmarks[15].y])  # Muñeca izquierda
        p2 = np.array([landmarks[17].x, landmarks[17].y])  # Dedos
        return np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))

# Función para procesar el video y obtener los códigos posturales más altos
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)

    # Diccionario para almacenar el código postural más alto de cada parte del cuerpo
    highest_postural_codes = {
        "espalda": 0,
        "cuello": 0,
        "piernas": 0,
        "brazos": 0,
        "antebrazos": 0,
        "muñeca": 0
}
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir a RGB para Mediapipe
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image_rgb)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks.landmark

            # Procesar los ángulos para las partes del cuerpo
            trunk_angle = calculate_angle(landmarks, "trunk")
            neck_angle = calculate_angle(landmarks, "neck")
            leg_angle = calculate_angle(landmarks, "leg")
            upper_arm_angle = calculate_angle(landmarks, "upper_arm")
            lower_arm_angle = calculate_angle(landmarks, "lower_arm")
            wrist_angle = calculate_angle(landmarks, "wrist")

            # Obtener los códigos posturales
            trunk_code = obtener_codigo_postural(trunk_angle, "espalda")
            neck_code = obtener_codigo_postural(neck_angle, "cuello")
            leg_code = obtener_codigo_postural(leg_angle, "piernas")
            arm_code = obtener_codigo_postural(upper_arm_angle, "brazos")
            forearm_code = obtener_codigo_postural(lower_arm_angle, "antebrazos")
            wrist_code = obtener_codigo_postural(wrist_angle, "muñeca")

            # Actualizar el código postural más alto
            highest_postural_codes["cuello"] = max(highest_postural_codes["cuello"], neck_code or 1)
            highest_postural_codes["espalda"] = max(highest_postural_codes["espalda"], trunk_code or 1)
            highest_postural_codes["piernas"] = max(highest_postural_codes["piernas"], leg_code or 1)
            highest_postural_codes["brazos"] = max(highest_postural_codes["brazos"], arm_code or 1)
            highest_postural_codes["antebrazos"] = max(highest_postural_codes["antebrazos"], forearm_code or 1)
            highest_postural_codes["muñeca"] = max(highest_postural_codes["muñeca"], wrist_code or 1)

        # Mostrar el video procesado
        cv2.imshow('Processed Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    for key in highest_postural_codes:
        if not highest_postural_codes[key] or highest_postural_codes[key] is None:
            highest_postural_codes[key] = 1  # Asignar 1 como valor predeterminado

    # Después de procesar el video, calcular las puntuaciones globales
    puntuacion_grupo_A = calcular_puntuacion_global_A(
        highest_postural_codes["espalda"],
        highest_postural_codes["cuello"],
        highest_postural_codes["piernas"]
    )
    
    puntuacion_grupo_B = calcular_puntuacion_global_grupo_B(
        highest_postural_codes["brazos"],
        highest_postural_codes["antebrazos"],
        highest_postural_codes["muñeca"]
    )

    # Calcular la puntuación final
    puntuacion_final = calcular_puntuacion_final(puntuacion_grupo_A, puntuacion_grupo_B)

    # Determinar el nivel de riesgo
    riesgo = determinar_nivel_riesgo(puntuacion_final)

    # Mostrar los resultados finales
    print("Resultados Finales:")
    print(f"Puntuación Grupo A: {puntuacion_grupo_A}")
    print(f"Puntuación Grupo B: {puntuacion_grupo_B}")
    print(f"Puntuación Final: {puntuacion_final}")
    print(f"Nivel de Riesgo: {riesgo['Nivel']}")
    print(f"Riesgo: {riesgo['Riesgo']}")
    print(f"Recomendación: {riesgo['Actuación']}")

    return highest_postural_codes

def calcular_puntuacion_global_A(trunk_code, neck_code, knee_code):
    """
    Calcula la puntuación global del Grupo A utilizando la matriz de calificación REBA.
    """
    # Matriz de calificación REBA para el Grupo A (2 dimensiones: espalda, cuello y piernas)
    matriz_calificacion_a = [
        [1, 2, 3, 4, 1, 2, 3, 4, 3, 3, 5, 6],
        [2, 3, 4, 5, 3, 4, 5, 6, 4, 5, 6, 7],
        [2, 4, 5, 6, 4, 5, 6, 7, 5, 6, 7, 8],
        [3, 5, 6, 7, 5, 6, 7, 8, 6, 7, 8, 9],
        [4, 6, 7, 8, 6, 7, 8, 9, 7, 8, 9, 9]
    ]

    # Convertimos los códigos de postura en índices válidos (restando 1 porque las matrices empiezan desde 1)
    trunk_index = trunk_code - 1
    neck_index = neck_code - 1
    knee_index = knee_code - 1

    # Obtenemos el valor en la intersección de la matriz usando los 3 índices
    puntuacion_grupo_A = matriz_calificacion_a[trunk_index][neck_index + knee_index]

    return puntuacion_grupo_A


#*OBTENER PUNTUACION GLOBAL DEL GRUPO B*
def calcular_puntuacion_global_grupo_B(arm_code, forearm_code, wrist_code):
    """
    Calcula la puntuación global del Grupo B utilizando la matriz de calificación para brazo,
    antebrazo y muñeca.
    """
    # Matriz de calificación REBA para el Grupo B (2 dimensiones: brazo, antebrazo y muñeca)
    matriz_calificacion_b = [
    [1, 2, 2, 1, 2, 3],
    [1, 2, 3, 2, 3, 4],
    [3, 4, 5, 4, 5, 5],
    [4, 5, 5, 5, 6, 7],
    [6, 7, 8, 7, 8, 8],
    [7, 8, 8, 8, 9, 9]
    ]

    # Convertimos los códigos de postura en índices válidos (restando 1 porque las matrices empiezan desde 1)
    arm_index = arm_code - 1
    forearm_index = forearm_code - 1
    wrist_index = wrist_code - 1

    # Obtenemos el valor en la intersección de la matriz utilizando los índices correspondientes
    puntuacion_grupo_B = matriz_calificacion_b[arm_index][forearm_index + wrist_index]

    return puntuacion_grupo_B


def calcular_puntuacion_final(puntuacion_grupo_A, puntuacion_grupo_B):
    """
    Calcula la puntuación final combinando las puntuaciones de los Grupos A y B
    usando la matriz de calificación REBA.
    """
    # Matriz de calificación REBA (PUNTUACION FINAL)
    matriz_calificacion_c = [
        [1, 1, 1, 2, 3, 3, 4, 5, 6, 7, 7, 7],
        [1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 7, 8],
        [2, 3, 3, 3, 4, 5, 6, 7, 7, 8, 8, 8],
        [3, 4, 4, 4, 5, 6, 7, 8, 8, 9, 9, 9],
        [4, 4, 4, 5, 6, 7, 8, 8, 9, 9, 9, 9],
        [6, 6, 6, 7, 8, 8, 9, 9, 10, 10, 10, 10],
        [7, 7, 7, 8, 9, 9, 9, 10, 10, 11, 11, 11],
        [8, 8, 8, 9, 10, 10, 10, 10, 10, 11, 11, 11],
        [9, 9, 9, 10, 10, 10, 11, 11, 11, 12, 12, 12],
        [10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 12],
        [11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12],
        [12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12]
    ]

    # Convertimos las puntuaciones a índices válidos (restando 1)
    puntuacion_a_index = puntuacion_grupo_A - 1
    puntuacion_b_index = puntuacion_grupo_B - 1

    # Obtenemos la puntuación final en la intersección de la matriz
    puntuacion_final = matriz_calificacion_c[puntuacion_a_index][puntuacion_b_index]

    return puntuacion_final


def determinar_nivel_riesgo(puntuacion_final):
    """
    Determina el nivel de riesgo basado en la puntuación final calculada por la matriz REBA.
    """
    if puntuacion_final == 1:
        return {"Nivel": "Inapreciable", "Riesgo": 0, "Actuación": "No es necesaria actuación"}
    elif puntuacion_final in [2, 3]:
        return {"Nivel": "Bajo", "Riesgo": 1, "Actuación": "Puede ser necesaria la actuación."}
    elif puntuacion_final >= 4 and puntuacion_final <= 7:
        return {"Nivel": "Medio", "Riesgo": 2, "Actuación": "Es necesaria la actuación."}
    elif puntuacion_final >= 8 and puntuacion_final <= 10:
        return {"Nivel": "Alto", "Riesgo": 3, "Actuación": "Es necesaria la actuación cuanto antes."}
    elif puntuacion_final >= 11 and puntuacion_final <= 15:
        return {"Nivel": "Muy alto", "Riesgo": 4, "Actuación": "Es necesaria la actuación de inmediato."}
    else:
        return {"Nivel": "Desconocido", "Riesgo": -1, "Actuación": "No se puede determinar el riesgo."}
