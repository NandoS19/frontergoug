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
    Procesa un video para calcular ángulos corporales y determinar el nivel de riesgo OWAS.
    :param filepath: Ruta completa del archivo de video.
    :return: Diccionario con ángulos promedio y puntajes OWAS.
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(filepath)
    
    if not cap.isOpened():
        raise ValueError("No se puede abrir el archivo de video")
    
    angles = {"back": [], "arms": [], "legs": []}
    
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
            
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                   landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            

            if not all([shoulder, elbow, wrist, hip, knee, ankle]):
                raise ValueError("No se detectaron todos los puntos clave del cuerpo en el video.")
         
            # Calcular ángulos
            back_angle = calculate_angle(knee, hip, shoulder) # Ángulo de espalda
            arms_angle = calculate_angle(shoulder, elbow, wrist) # Ángulo de brazos
            legs_angle = calculate_angle(hip, knee, ankle) # Ángulo de piernas
                        
            angles["back"].append(back_angle)
            angles["arms"].append(arms_angle)
            angles["legs"].append(legs_angle)            

    cap.release()
    pose.close()

    # Promediar los ángulos
    averaged_angles = {key: round(np.mean(values), 2) for key, values in angles.items() if values}
    
    return averaged_angles