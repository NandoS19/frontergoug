import cv2
import mediapipe as mp
import numpy as np

def calculate_angle(point1, point2, point3):
    """
    Calcula el ángulo entre tres puntos en 2D.
    """
    a = np.array(point1)
    b = np.array(point2)
    c = np.array(point3)
    ab = a - b
    bc = c - b
    cosine_angle = np.dot(ab, bc) / (np.linalg.norm(ab) * np.linalg.norm(bc))
    return round(np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0))), 2)

def classify_owas(angles):
    """
    Clasifica las posturas usando el método OWAS basado en ángulos calculados.
    :param angles: Diccionario con los ángulos corporales.
    :return: Categoría de riesgo OWAS.
    """
    hip_angle = angles.get("hip", 0)
    trunk_angle = angles.get("trunk", 0)
    arm_angle = angles.get("arm", 0)

    # Clasificación según los ángulos calculados
    if trunk_angle < 20 and hip_angle < 30 and arm_angle < 45:
        return "Riesgo 1: Postura aceptable"
    elif 20 <= trunk_angle <= 60 or hip_angle >= 30 or arm_angle >= 45:
        return "Riesgo 2: Necesita revisión"
    elif trunk_angle > 60 or hip_angle > 60 or arm_angle > 90:
        return "Riesgo 3: Corrección requerida pronto"
    else:
        return "Riesgo 4: Corrección urgente"

def process_video(filepath):
    """
    Procesa un video para calcular ángulos corporales y clasificar según OWAS.
    :param filepath: Ruta completa del archivo de video.
    :return: Diccionario con evaluaciones OWAS por cuadro.
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(filepath)

    if not cap.isOpened():
        raise ValueError("No se puede abrir el archivo de video")

    owas_results = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Procesar el cuadro
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        if results.pose_landmarks:
            # Extraer puntos clave del cuerpo
            landmarks = results.pose_landmarks.landmark

            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]

            # Calcular ángulos
            hip_angle = calculate_angle(left_knee, left_hip, left_shoulder)
            trunk_angle = calculate_angle([0, 1], left_hip, left_shoulder)  # Aproximación del tronco vertical
            arm_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

            # Clasificar postura con OWAS
            angles = {"hip": hip_angle, "trunk": trunk_angle, "arm": arm_angle}
            owas_category = classify_owas(angles)
            owas_results.append(owas_category)

    cap.release()
    pose.close()

    return owas_results

# Ejemplo de uso
video_path = "ruta/del/video.mp4"
resultados_owas = process_video(video_path)

# Mostrar resultados
print("Clasificación OWAS por cuadro:")
for idx, resultado in enumerate(resultados_owas):
    print(f"Cuadro {idx + 1}: {resultado}")