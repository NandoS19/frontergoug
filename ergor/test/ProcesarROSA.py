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

def process_video(filepath):
    """
    Procesa un video para calcular ángulos corporales promedio.
    :param filepath: Ruta completa del archivo de video.
    :return: Diccionario con ángulos promedio.
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(filepath)
    
    if not cap.isOpened():
        raise ValueError("No se puede abrir el archivo de video")
    else:
        angles = {"hip": [], "shoulder": [], "elbow": [], "wrist": []}

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
            left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]

            # Calcular ángulos
            angles["hip"].append(calculate_angle(left_knee, left_hip, left_shoulder))
            angles["shoulder"].append(calculate_angle(left_hip, left_shoulder, left_elbow))
            angles["elbow"].append(calculate_angle(left_shoulder, left_elbow, left_wrist))

    cap.release()
    pose.close()

    # Promediar los ángulos
    averaged_angles = {key: round(np.mean(values), 2) for key, values in angles.items() if values}
    return averaged_angles
