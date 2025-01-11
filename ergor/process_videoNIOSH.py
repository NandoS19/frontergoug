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
    Procesa un video para calcular factores relevantes para NIOSH.
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(filepath)

    horizontal_distances = []
    vertical_distances = []
    asymmetry_angles = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Procesar el cuadro
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Puntos clave
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_hand = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

            # Calcular distancias horizontales y verticales
            horizontal_distance = np.abs(left_hand[0] - left_hip[0])
            vertical_distance = np.abs(left_hand[1] - left_hip[1])

            # Calcular ángulo de asimetría (rotación del torso)
            asymmetry_angle = calculate_angle(left_hip, left_shoulder, left_hand)

            # Guardar en las listas
            horizontal_distances.append(horizontal_distance)
            vertical_distances.append(vertical_distance)
            asymmetry_angles.append(asymmetry_angle)

    cap.release()
    pose.close()

    # Promediar los valores
    results = {
        "horizontal_distance": round(np.mean(horizontal_distances), 2),
        "vertical_distance": round(np.mean(vertical_distances), 2),
        "asymmetry_angle": round(np.mean(asymmetry_angles), 2)
    }
    return results
