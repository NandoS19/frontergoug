import google.generativeai as genai
from ergor.models import User, RosaScore, NioshScore
from ergor import db

# Configurar la API de Google Generative AI
genai.configure(api_key="AIzaSyAo46Co2yniw1aQDFWbcZsfsVipbv0v_zM")

def generate_plan(user_id, method):
    """
    Genera un plan de mejora y diagnóstico usando la API de Google Generative AI.
    :param user_id: ID del usuario.
    :param method: Método de evaluación (ROSA, NIOSH, etc.).
    :return: Diccionario con el diagnóstico y plan de mejora.
    """
    user = User.query.get(user_id)
    if not user:
        return {"error": "Usuario no encontrado"}

    # Crear el prompt basado en el método
    prompt = ""
    if method == "ROSA":
        # Recuperar resultados ROSA
        rosa_score = RosaScore.query.filter_by(user_id=user_id).order_by(RosaScore.evaluation_date.desc()).first()
        if not rosa_score:
            return {"error": "No se encontraron resultados para el método ROSA"}

        prompt = (
            f"Usuario: {user.username}\n"
            f"Puntajes ROSA:\n"
            f"- Puntaje de silla: {rosa_score.chair_score}\n"
            f"- Puntaje de monitor: {rosa_score.monitor_score}\n"
            f"- Puntaje de teclado: {rosa_score.keyboard_score}\n"
            f"- Puntaje de teléfono: {rosa_score.phone_score}\n"
            f"- Puntaje total: {rosa_score.total_score}\n\n"
            f"Con base en estos resultados, genera un diagnóstico y un plan de mejora ergonómico detallado."
        )
    elif method == "NIOSH":
        # Recuperar resultados NIOSH
        niosh_score = NioshScore.query.filter_by(user_id=user_id).order_by(NioshScore.evaluation_date.desc()).first()
        if not niosh_score:
            return {"error": "No se encontraron resultados para el método NIOSH"}

        prompt = (
            f"Usuario: {user.username}\n"
            f"Puntajes NIOSH:\n"
            f"- Peso de la carga: {niosh_score.load_weight} kg\n"
            f"- Distancia horizontal: {niosh_score.horizontal_distance} m\n"
            f"- Distancia vertical: {niosh_score.vertical_distance} m\n"
            f"- Ángulo de asimetría: {niosh_score.asymmetry_angle} grados\n"
            f"- Frecuencia: {niosh_score.frequency} levantamientos/minuto\n"
            f"- RWL: {niosh_score.rwl} kg\n\n"
            f"Con base en estos resultados, genera un diagnóstico y un plan de mejora ergonómico detallado."
        )
    else:
        return {"error": "Método no soportado"}

    # Enviar el prompt a la API
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        return {"diagnostic_plan": response.text}
    except Exception as e:
        return {"error": f"Error al generar el plan: {str(e)}"}
