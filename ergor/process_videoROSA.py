import cv2
import mediapipe as mp
import numpy as np
from datetime import datetime
from ergor import db
from models import RosaScore

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
    angle = np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

    return round(angle, 2)

def process_video(filepath, user_id):
    """
    Procesa un video para calcular puntajes según el método ROSA.
    Guarda los resultados en la base de datos.
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(filepath)

    # Inicializar puntajes acumulados
    chair_score = 0
    monitor_score = 0
    phone_score = 0
    keyboard_score = 0
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Puntos clave relevantes
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
            left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                          landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            # Calcular ángulos
            shoulder_angle = calculate_angle(left_hip, left_shoulder, left_elbow)
            elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
            hip_angle = calculate_angle(left_knee, left_hip, left_shoulder)

            # Asignar puntajes según reglas ROSA (simplificadas)
            chair_score += 1 if shoulder_angle > 20 else 0
            monitor_score += 1 if hip_angle > 30 else 0
            keyboard_score += 1 if elbow_angle > 90 else 0

            frame_count += 1

    cap.release()
    pose.close()

    # Calcular puntajes finales
    chair_score = round(chair_score / frame_count, 2)
    monitor_score = round(monitor_score / frame_count, 2)
    keyboard_score = round(keyboard_score / frame_count, 2)
    phone_score = 1  # Puntaje fijo de ejemplo
    total_score = round(chair_score + monitor_score + keyboard_score + phone_score, 2)

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
        "phone_score": phone_score,
        "keyboard_score": keyboard_score,
        "total_score": total_score
    }


