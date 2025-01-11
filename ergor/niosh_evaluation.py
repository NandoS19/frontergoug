def evaluate_niosh(load_weight, horizontal_distance, vertical_distance, asymmetry_angle, frequency):
    """
    Calcula el RWL y el índice de levantamiento para NIOSH.
    """
    # Constantes
    LC = 23  # Constante de carga en kg

    # Multiplicadores
    HM = 1 - (0.003 * horizontal_distance * 100)  # Convertir a cm
    VM = (vertical_distance * 100 - 75) / 75
    VM = 1 - abs(VM) if 0 <= vertical_distance <= 1.5 else 0
    AM = 1 - (0.0032 * asymmetry_angle)
    FM = 0.95 if frequency < 10 else (0.85 if frequency < 20 else 0.7)

    # Verificar límites
    HM = max(HM, 0)
    VM = max(VM, 0)
    AM = max(AM, 0)
    FM = max(FM, 0)

    # RWL
    RWL = LC * HM * VM * AM * FM

    # Índice de levantamiento
    LI = load_weight / RWL

    return {
        "RWL": round(RWL, 2),
        "LI": round(LI, 2),
        "risk_level": "Alto" if LI > 3 else "Moderado" if LI > 1 else "Bajo"
    }
