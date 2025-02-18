import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple, Optional

def calculate_angle(point1: Tuple[float, float], 
                   point2: Tuple[float, float], 
                   point3: Tuple[float, float]) -> float:
    """
    Calcula el ángulo entre tres puntos en 2D con mejor precisión y manejo de casos extremos.
    
    Args:
        point1: Primer punto (x, y)
        point2: Punto central (x, y)
        point3: Tercer punto (x, y)
    
    Returns:
        float: Ángulo en grados redondeado a 2 decimales
    """
    # Convertir a arrays numpy y asegurar tipo float64 para mejor precisión
    a = np.array(point1, dtype=np.float64)
    b = np.array(point2, dtype=np.float64)
    c = np.array(point3, dtype=np.float64)
    
    # Calcular vectores
    ab = a - b
    bc = c - b
    
    # Normalizar vectores para mejorar la precisión numérica
    ab_norm = ab / np.linalg.norm(ab)
    bc_norm = bc / np.linalg.norm(bc)
    
    # Calcular el ángulo usando el producto punto
    cosine_angle = np.dot(ab_norm, bc_norm)
    
    # Manejar casos extremos debido a errores de redondeo
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
    
    Args:
        point1: Primer punto (x, y)
        point2: Segundo punto (x, y)
        frame_dimensions: Dimensiones del frame (width, height) para normalización
    
    Returns:
        float: Distancia normalizada redondeada a 2 decimales
    """
    a = np.array(point1, dtype=np.float64)
    b = np.array(point2, dtype=np.float64)
    distance = np.linalg.norm(a - b)
    
    if frame_dimensions:
        # Normalizar usando la diagonal del frame como referencia
        diagonal = np.sqrt(frame_dimensions[0]**2 + frame_dimensions[1]**2)
        distance = (distance / diagonal) * 100
        
    return round(distance, 2)

def process_video(filepath: str, sample_rate: int = 1) -> Dict[str, float]:
    """
    Procesa un video para calcular ángulos corporales promedio con mejor manejo de errores
    y procesamiento más robusto.
    
    Args:
        filepath: Ruta del archivo de video
        sample_rate: Procesar 1 de cada N frames (default: 1)
    
    Returns:
        Dict[str, float]: Diccionario con los ángulos y distancias promedio
    
    Raises:
        ValueError: Si no se puede abrir el video o no se detectan poses
    """
    # Inicializar MediaPipe con configuración optimizada
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=2  # Usar modelo más preciso
    )
    
    # Inicializar captura de video
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        raise ValueError("No se puede abrir el archivo de video")
    
    # Estructuras para almacenar mediciones
    measurements = {
        "hip": [], "shoulder": [], "elbow": [], "wrist": [],
        "knee": [], "neck": [], "back": [], "seat_depth": [],
        "monitor_distance": [], "phone_distance": []
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
            
        # Procesar frame
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
    
    cap.release()
    pose.close()
    
    if valid_frames == 0:
        raise ValueError("No se detectaron poses válidas en el video")
    
    # Calcular promedios y aplicar filtrado de valores atípicos
    averaged_measurements = {}
    for key, values in measurements.items():
        if values:
            # Filtrar valores atípicos usando el rango intercuartil
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            filtered_values = [x for x in values if lower_bound <= x <= upper_bound]
            
            # Calcular promedio de valores filtrados
            averaged_measurements[key] = round(np.mean(filtered_values), 2)
    
    return averaged_measurements