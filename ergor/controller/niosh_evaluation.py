def evaluate_niosh(load_weight, horizontal_distance, vertical_distance, asymmetry_angle, frequency, displacement_distance, grip_quality):
    """
    Calcula el RWL y el índice de levantamiento para NIOSH, incluyendo displacement_distance y grip_quality.
    """
    # Constantes
    LC = 23  # Constante de carga en kg

    # Multiplicadores
    HM = 1 - (0.003 * horizontal_distance * 100)  # Convertir a cm
    VM = (vertical_distance * 100 - 75) / 75
    VM = 1 - abs(VM) if 0 <= vertical_distance <= 1.5 else 0
    DM = 0.82 / displacement_distance if displacement_distance > 0 else 0
    AM = 1 - (0.0032 * asymmetry_angle)
    FM = 0.95 if frequency < 10 else (0.85 if frequency < 20 else 0.7)
    CM = 1.0 if grip_quality == "bueno" else (0.95 if grip_quality == "regular" else 0.9)

    # Verificar límites
    HM = max(HM, 0)
    VM = max(VM, 0)
    DM = max(DM, 0)
    AM = max(AM, 0)
    FM = max(FM, 0)

    # RWL
    RWL = LC * HM * VM * DM * AM * FM * CM

    # Índice de levantamiento
    LI = load_weight / RWL

    return {
    "RWL": round(RWL, 2),
    "LI": round(LI, 2), #Se asegura de retornar LI
    "risk_level": "Alto" if LI > 3 else "Moderado" if LI > 1 else "Bajo",
    "horizontal_distance": round(horizontal_distance, 2),
    "vertical_distance": round(vertical_distance, 2),
    "asymmetry_angle": round(asymmetry_angle, 2),
    "displacement_distance": round(displacement_distance, 2),
    "grip_quality": grip_quality,
    "load_weight": round(load_weight, 2),  # Peso de la carga
    "frequency": frequency  # Frecuencia de levantamiento
    
}
