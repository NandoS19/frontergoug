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

def infer_grip_quality(asymmetry_angle, displacement_distance):
    """
    Infiera la calidad del agarre basado en el ángulo de asimetría y la distancia de desplazamiento.
    """
    # Lógica simple para determinar la calidad del agarre
    if asymmetry_angle > 20 or displacement_distance > 0.6:
        return "malo"
    elif 10 < asymmetry_angle <= 20 or 0.3 < displacement_distance <= 0.6:
        return "regular"
    else:
        return "bueno"

def process_video(filepath):
    """
    Procesa un video para calcular factores relevantes para NIOSH e inferir grip_quality.
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(filepath)

    horizontal_distances = []
    vertical_distances = []
    asymmetry_angles = []

    initial_vertical_position = None
    final_vertical_position = None

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

            # Registrar la posición inicial y final de la mano (vertical)
            if initial_vertical_position is None:
                initial_vertical_position = left_hand[1]
            final_vertical_position = left_hand[1]

            # Calcular ángulo de asimetría (rotación del torso)
            asymmetry_angle = calculate_angle(left_hip, left_shoulder, left_hand)

            # Guardar en las listas
            horizontal_distances.append(horizontal_distance)
            vertical_distances.append(vertical_distance)
            asymmetry_angles.append(asymmetry_angle)

    cap.release()
    pose.close()

    # Calcular desplazamiento vertical
    displacement_distance = abs(final_vertical_position - initial_vertical_position) if initial_vertical_position is not None and final_vertical_position is not None else 0

    # Inferir calidad del agarre
    avg_asymmetry_angle = np.mean(asymmetry_angles)
    grip_quality = infer_grip_quality(avg_asymmetry_angle, displacement_distance)

    # Promediar los valores
    results = {
        "horizontal_distance": round(np.mean(horizontal_distances), 2),
        "vertical_distance": round(np.mean(vertical_distances), 2),
        "asymmetry_angle": round(avg_asymmetry_angle, 2),
        "displacement_distance": round(displacement_distance, 2),
        "grip_quality": grip_quality
    }
    return results