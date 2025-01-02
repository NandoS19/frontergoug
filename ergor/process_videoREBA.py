import cv2
import mediapipe as mp
import numpy as np
import math

# Inicializamos Mediapipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    """
    Calcula el ángulo entre tres puntos
    a, b, c: coordenadas (x, y) de los puntos
    """
    a = np.array(a)  # Punto inicial
    b = np.array(b)  # Punto central
    c = np.array(c)  # Punto final

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)  # Reemplaza por la ruta de tu video

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convertir la imagen de BGR a RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image_rgb)

        if result.pose_landmarks:
            landmarks = result.pose_landmarks.landmark

            # Procesar y calcular para el grupo A y B
            process_group_a(landmarks, frame)
            process_group_b(landmarks, frame)

        # Mostrar el video procesado
        cv2.imshow('Video Procesado', frame)
    cap.release()
    cv2.destroyAllWindows()

#GRUPO A
def assign_postural_code_trunk(trunk_angle, is_rotated_or_laterally_inclined):
    """
    Asigna el código postural al tronco según el ángulo calculado
    """
    code = 0
    if trunk_angle <= 20:
        code = 1  # Erguido
    elif 20 < trunk_angle <= 60:
        code = 3  # Flexión moderada
    elif trunk_angle > 60:
        code = 4  # Flexión severa
    elif trunk_angle < 0:
        code = 2  # Extensión

    # Sumar +1 si hay rotación o inclinación lateral
    if is_rotated_or_laterally_inclined:
        code += 1

    return code

def assign_postural_code_neck(neck_angle, is_rotated_or_laterally_inclined):
    """
    Asigna el código postural al cuello según el ángulo calculado
    """
    code = 0
    if 0 <= neck_angle <= 20:
        code = 1  # Flexión leve
    elif neck_angle > 20:
        code = 2  # Flexión severa

    # Sumar +1 si hay rotación o inclinación lateral
    if is_rotated_or_laterally_inclined:
        code += 1

    return code

def assign_postural_code_legs(knee_angle):
    """
    Asigna el código postural a las piernas según el ángulo calculado
    """
    code = 0
    if 30 <= knee_angle <= 60:
        code = 1  # Flexión leve
    elif knee_angle > 60:
        code = 2  # Flexión severa

    return code

#GRUPO N
def assign_postural_code_arm(elbow_angle, is_rotated, is_shoulders_elevated, is_arm_support):
    """
    Asigna el código postural para el brazo según el ángulo calculado y las condiciones adicionales.
    """
    # Asignación inicial según el ángulo
    if -20 <= elbow_angle <= 20:
        code = 1  # De 20° extensión a 20° flexión
    elif (elbow_angle > 20 and elbow_angle <= 45) or (elbow_angle < -20 and elbow_angle >= -45):
        code = 2  # Extensión > 20° o flexión > 20° y <= 45°
    elif (elbow_angle > 45 and elbow_angle <= 90) or (elbow_angle < -45 and elbow_angle >= -90):
        code = 3  # Flexión > 45° y <= 90°
    else:
        code = 4  # Flexión > 90°

    # Condiciones adicionales
    
    if is_shoulders_elevated:
        code += 1  # Sumar 1 si los hombros están elevados
    if is_arm_support:
        code -= 1  # Restar 1 si hay un punto de apoyo en los brazos

    return code

def assign_postural_code_forearm(forearm_angle):
    """
    Asigna el código postural al antebrazo según el ángulo de flexión.
    """
    code = 0
    if 60 <= forearm_angle <= 100:
        code = 1  # Flexión moderada
    elif forearm_angle < 60 or forearm_angle > 100:
        code = 2  # Flexión severa o ligera
    return code

def assign_postural_code_wrist(wrist_angle):
    """
    Asigna el código postural a la muñeca según el ángulo de flexión o extensión.
    """
    code = 0
    if 0 < wrist_angle < 15:
        code = 1  # Flexión/Extensión moderada
    elif wrist_angle >= 15:
        code = 2  # Flexión/Extensión severa
    return code

def check_rotation_or_lateral_inclination(landmarks):
    """
    Determina si hay rotación o inclinación lateral del tronco
    """
    left_shoulder = np.array([landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y])
    right_shoulder = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y])
    left_hip = np.array([landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y])
    right_hip = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y])

    # Cálculo de diferencias horizontales y verticales
    shoulder_diff = np.abs(left_shoulder[1] - right_shoulder[1])
    hip_diff = np.abs(left_hip[1] - right_hip[1])

    # Si las diferencias exceden un umbral, hay rotación o inclinación lateral
    threshold = 1
    return shoulder_diff > threshold or hip_diff > threshold

def check_head_rotation_or_lateral_inclination(landmarks):
    """
    Determina si hay rotación o inclinación lateral de la cabeza
    """
    left_ear = np.array([landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x, landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y])
    right_ear = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value].y])

    # Cálculo de diferencias verticales
    ear_diff = np.abs(left_ear[1] - right_ear[1])

    # Si la diferencia excede un umbral, hay rotación o inclinación lateral
    threshold = 1
    return ear_diff > threshold

#GRUPO A
def process_group_a(landmarks, image):
    """
    Procesa los ángulos del Grupo A: Tronco, cuello y piernas
    """
    # Coordenadas relevantes
    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
    head = [landmarks[mp_pose.PoseLandmark.NOSE.value].x, landmarks[mp_pose.PoseLandmark.NOSE.value].y]

    # Cálculo de ángulos
    trunk_angle = calculate_angle(shoulder, hip, knee)
    neck_angle = calculate_angle(shoulder, head, hip)
    knee_angle = calculate_angle(hip, knee, ankle)

    # Verificar rotación o inclinación lateral
    is_trunk_rotated_or_laterally_inclined = check_rotation_or_lateral_inclination(landmarks)
    is_neck_rotated_or_laterally_inclined = check_head_rotation_or_lateral_inclination(landmarks)

    # Asignación de códigos posturales
    trunk_code = assign_postural_code_trunk(trunk_angle, is_trunk_rotated_or_laterally_inclined)
    neck_code = assign_postural_code_neck(neck_angle, is_neck_rotated_or_laterally_inclined)
    knee_code = assign_postural_code_legs(knee_angle)

    # Calculamos la puntuación global
    puntuacion_global = calcular_puntuacion_global_A(trunk_code, neck_code, knee_code)

    # Dibujamos los ángulos, códigos y la puntuación en la imagen
    cv2.putText(image, f'Trunk: {int(trunk_angle)} (Code: {trunk_code})', tuple(np.multiply(hip, [image.shape[1], image.shape[0]]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(image, f'Neck: {int(neck_angle)} (Code: {neck_code})', tuple(np.multiply(head, [image.shape[1], image.shape[0]]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(image, f'Knee: {int(knee_angle)} (Code: {knee_code})', tuple(np.multiply(knee, [image.shape[1], image.shape[0]]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(image, f'Global Score: {puntuacion_global}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)


#GRUPO B

def check_shoulder_raised(landmarks):
    """
    Verifica si los hombros están elevados comparando las alturas de los hombros.
    """
    left_shoulder = np.array([landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y])
    right_shoulder = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y])
    
    # Umbral para considerar que un hombro está elevado
    threshold = 0.05
    return abs(left_shoulder[1] - right_shoulder[1]) > threshold

def check_support_in_arm(landmarks):
    """
    Determina si hay un punto de apoyo en el brazo (por ejemplo, al estar en el suelo o apoyado en una superficie).
    """
    left_wrist = np.array([landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y])
    right_wrist = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y])

    # Cualquier condición de contacto con el suelo (verificando si la muñeca está cerca de la superficie)
    threshold = 1
    return left_wrist[1] > threshold or right_wrist[1] > threshold


def process_group_b(landmarks, image):
    """
    Procesa los ángulos del Grupo B: Brazo, antebrazo, muñeca.
    """
    # Coordenadas relevantes
    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

    # Cálculo de ángulos
    elbow_angle = calculate_angle(shoulder, elbow, wrist)

    # Verificar si el hombro está elevado
    shoulder_raised = check_shoulder_raised(landmarks)

    # Verificar si hay un punto de apoyo en el brazo
    has_support = check_support_in_arm(landmarks)

    # Asignar el código postural del brazo
    arm_code = assign_postural_code_arm(elbow_angle, shoulder_raised, has_support)

    # Ahora, procesamos el antebrazo
    forearm_angle = calculate_angle(elbow, wrist, [landmarks[mp_pose.PoseLandmark.LEFT_HAND.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HAND.value].y])
    forearm_code = assign_postural_code_forearm(forearm_angle)

    # Ahora procesamos la muñeca
    wrist_angle = calculate_angle(elbow, wrist, [landmarks[mp_pose.PoseLandmark.LEFT_HAND.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HAND.value].y])
    wrist_code = assign_postural_code_wrist(wrist_angle)

    # Dibujamos los ángulos y códigos en la imagen
    cv2.putText(image, f'Elbow: {int(elbow_angle)} (Code: {arm_code})', tuple(np.multiply(elbow, [image.shape[1], image.shape[0]]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(image, f'Forearm: {int(forearm_angle)} (Code: {forearm_code})', tuple(np.multiply(elbow, [image.shape[1], image.shape[0]]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(image, f'Wrist: {int(wrist_angle)} (Code: {wrist_code})', tuple(np.multiply(wrist, [image.shape[1], image.shape[0]]).astype(int)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)



#**OBTENER PUNTUACION GLOBAL DEL GRUPO A**
def calcular_puntuacion_global_A(trunk_code, neck_code, knee_code):
    """
    Calcula la puntuación global del Grupo A utilizando la matriz de calificación REBA.
    """
    # Matriz de calificación REBA
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

    # Obtenemos el valor en la intersección de la matriz
    puntuacion_grupo_A = matriz_calificacion_a[trunk_index][neck_index + knee_index]
    
    return puntuacion_grupo_A

#**OBTENER PUNTUACION GLOBAL DEL GRUPO B**
def calcular_puntuacion_global_grupo_B(arm_code, forearm_code, wrist_code):
    """
    Calcula la puntuación global del Grupo B utilizando la matriz de calificación para brazo,
    antebrazo y muñeca.
    """
    # Matriz de calificación REBA para el Grupo B (debe ajustarse según las especificaciones)
    matriz_calificacion_b = [
        [1, 2, 3, 4],
        [2, 3, 4, 5],
        [3, 4, 5, 6],
        [4, 5, 6, 7],
    ]

    # Convertimos los códigos de postura en índices válidos (restando 1 porque las matrices empiezan desde 1)
    arm_index = arm_code - 1
    forearm_index = forearm_code - 1
    wrist_index = wrist_code - 1

    # Sumar los valores de las matrices para obtener la puntuación global
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

