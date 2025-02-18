import cv2
import mediapipe as mp
import numpy as np
import time

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

def process_video(filepath, sample_rate=30):
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
    
    posture_counts = {"back": {}, "arms": {}, "legs": {}}
    frame_count = 0
    start_time = time.time()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_time = time.time() - start_time
        if frame_time < sample_rate * frame_count:
            continue
        frame_count += 1
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
                        
            back_category = 1 if back_angle <= 20 else 2 if back_angle <= 45 else 3 if back_angle <= 60 else 4
            arms_category = 1 if arms_angle <= 45 else 2 if arms_angle <= 90 else 3
            legs_category = 1 if legs_angle <= 45 else 2 if legs_angle <= 90 else 3 if legs_angle <= 150 else 4
            
            posture_counts["back"].setdefault(back_category, 0)
            posture_counts["arms"].setdefault(arms_category, 0)
            posture_counts["legs"].setdefault(legs_category, 0)
            
            posture_counts["back"][back_category] += 1
            posture_counts["arms"][arms_category] += 1
            posture_counts["legs"][legs_category] += 1
    
    cap.release()
    pose.close()
    
    total_samples = frame_count
    posture_frequencies = {category: {key: round(value / total_samples * 100, 2)
                                      for key, value in counts.items()}
                            for category, counts in posture_counts.items()}
    
    risk_level = "Bajo"
    if any(freq >= 50 for freqs in posture_frequencies.values() for freq in freqs.values() if freq >= 50):
        risk_level = "Moderado"
    if any(freq >= 70 for freqs in posture_frequencies.values() for freq in freqs.values() if freq >= 70):
        risk_level = "Alto"
    if any(freq >= 90 for freqs in posture_frequencies.values() for freq in freqs.values() if freq >= 90):
        risk_level = "Muy Alto"
    
    return {"posture_frequencies": posture_frequencies, "risk_level": risk_level}