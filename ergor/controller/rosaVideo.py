import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple, Optional

def calculate_angle(point1: Tuple[float, float], 
                   point2: Tuple[float, float], 
                   point3: Tuple[float, float]) -> float:
    """
    Calcula el ángulo entre tres puntos en 2D con mejor precisión y manejo de casos extremos.
    """
    a = np.array(point1, dtype=np.float64)
    b = np.array(point2, dtype=np.float64)
    c = np.array(point3, dtype=np.float64)
    
    ab = a - b
    bc = c - b
    
    ab_norm = ab / np.linalg.norm(ab)
    bc_norm = bc / np.linalg.norm(bc)
    
    cosine_angle = np.dot(ab_norm, bc_norm)
    
    if cosine_angle > 1.0:
        cosine_angle = 1.0
    elif cosine_angle < -1.0:
        cosine_angle = -1.0
        
    angle = np.degrees(np.arccos(cosine_angle))
    return round(angle, 2)

def calculate_distance(point1: Tuple[float, float], 
                      point2: Tuple[float, float], 
                      frame_dimensions: Optional[Tuple[int, int]] = None) -> float:
    """
    Calcula la distancia normalizada entre dos puntos.
    """
    a = np.array(point1, dtype=np.float64)
    b = np.array(point2, dtype=np.float64)
    distance = np.linalg.norm(a - b)
    
    if frame_dimensions:
        diagonal = np.sqrt(frame_dimensions[0]**2 + frame_dimensions[1]**2)
        distance = (distance / diagonal) * 100
        
    return round(distance, 2)

def process_video(filepath: str, sample_rate: int = 1) -> Dict[str, float]:
    """
    Procesa un video para calcular ángulos corporales promedio y factores adicionales.
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=2
    )
    
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        raise ValueError("No se puede abrir el archivo de video")
    
    measurements = {
        "hip": [], "shoulder": [], "elbow": [], "wrist": [],
        "knee": [], "neck": [], "back": [], "seat_depth": [],
        "monitor_distance": [], "phone_distance": [],
        "feet_contact": [], "leg_space": [], "seat_height_adjustable": [],
        "seat_depth_adjustable": [], "armrest_separation": [], "armrest_surface": [],
        "armrest_adjustable": [], "work_surface_height": [], "backrest_adjustable": [],
        "monitor_lateral_deviation": [], "document_holder": [], "monitor_glare": [],
        "monitor_too_far": [], "phone_shoulder": [], "phone_hands_free": [],
        "wrist_deviation": [], "keyboard_height": [], "keyboard_adjustable": []
    }
    
    frame_count = 0
    valid_frames = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        if frame_count % sample_rate != 0:
            continue
            
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_height, frame_width = frame.shape[:2]
        results = pose.process(frame_rgb)
        
        if results.pose_landmarks:
            valid_frames += 1
            landmarks = results.pose_landmarks.landmark
            
            # Extraer puntos clave normalizados
            left_shoulder = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * frame_width,
                           landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * frame_height)
            left_elbow = (landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * frame_width,
                         landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * frame_height)
            left_wrist = (landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * frame_width,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * frame_height)
            left_hip = (landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x * frame_width,
                       landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y * frame_height)
            left_knee = (landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x * frame_width,
                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y * frame_height)
            left_ankle = (landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * frame_width,
                         landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y * frame_height)
            nose = (landmarks[mp_pose.PoseLandmark.NOSE.value].x * frame_width,
                   landmarks[mp_pose.PoseLandmark.NOSE.value].y * frame_height)
            left_index = (landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value].x * frame_width,
                         landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value].y * frame_height)
            
            # Calcular punto medio de la columna
            mid_spine = ((left_hip[0] + left_shoulder[0]) / 2,
                        (left_hip[1] + left_shoulder[1]) / 2)
            
            # Calcular y almacenar ángulos
            measurements["hip"].append(calculate_angle(left_knee, left_hip, left_shoulder))
            measurements["shoulder"].append(calculate_angle(left_hip, left_shoulder, left_elbow))
            measurements["elbow"].append(calculate_angle(left_shoulder, left_elbow, left_wrist))
            measurements["wrist"].append(calculate_angle(left_elbow, left_wrist, left_index))
            measurements["knee"].append(calculate_angle(left_ankle, left_knee, left_hip))
            measurements["neck"].append(calculate_angle(left_shoulder, nose, mid_spine))
            measurements["back"].append(calculate_angle(left_hip, mid_spine, left_shoulder))
            
            # Calcular y almacenar distancias normalizadas
            frame_dims = (frame_width, frame_height)
            measurements["seat_depth"].append(calculate_distance(left_hip, left_knee, frame_dims))
            measurements["monitor_distance"].append(calculate_distance(nose, left_shoulder, frame_dims))
            measurements["phone_distance"].append(calculate_distance(left_shoulder, left_wrist, frame_dims))
            
            # Estimación de factores adicionales (ejemplos)
            measurements["feet_contact"].append(1 if left_ankle[1] < frame_height * 0.9 else 0)  # Suposición
            measurements["leg_space"].append(1 if calculate_distance(left_knee, left_hip, frame_dims) > 10 else 0)  # Suposición
            measurements["seat_height_adjustable"].append(1)  # Suposición: ajustable
            measurements["seat_depth_adjustable"].append(1)  # Suposición: ajustable
            measurements["armrest_separation"].append(0)  # Suposición: no separados
            measurements["armrest_surface"].append(0)  # Suposición: superficie no dura
            measurements["armrest_adjustable"].append(1)  # Suposición: ajustables
            measurements["work_surface_height"].append(0)  # Suposición: no demasiado alta
            measurements["backrest_adjustable"].append(1)  # Suposición: ajustable
            measurements["monitor_lateral_deviation"].append(0)  # Suposición: no desviada
            measurements["document_holder"].append(1)  # Suposición: hay atril
            measurements["monitor_glare"].append(0)  # Suposición: no hay brillos
            measurements["monitor_too_far"].append(0)  # Suposición: no muy lejos
            measurements["phone_shoulder"].append(0)  # Suposición: no sujetado con hombro
            measurements["phone_hands_free"].append(1)  # Suposición: manos libres
            measurements["wrist_deviation"].append(0)  # Suposición: no desviadas
            measurements["keyboard_height"].append(0)  # Suposición: no demasiado alto
            measurements["keyboard_adjustable"].append(1)  # Suposición: ajustable
    
    cap.release()
    pose.close()
    
    if valid_frames == 0:
        raise ValueError("No se detectaron poses válidas en el video")
    
    # Calcular promedios y aplicar filtrado de valores atípicos
    averaged_measurements = {}
    for key, values in measurements.items():
        if values:
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            filtered_values = [x for x in values if lower_bound <= x <= upper_bound]
            averaged_measurements[key] = round(np.mean(filtered_values), 2)
    
    return averaged_measurements