import google.generativeai as genai
from llamaapi import LlamaAPI
import openai
from ergor.models import User, RosaScore, NioshScore, OwasScore, RebaScore
from ergor import db

# Configurar las APIs
genai.configure(api_key="AIzaSyAo46Co2yniw1aQDFWbcZsfsVipbv0v_zM")  # API de Google Generative AI
llama = LlamaAPI("LA-05ca3abe055d4847aebd6b034374da2ff5a07974966e418e9d7f72b18635c32b")  # Llama API
#llave de api openai falta aqui, por motivo de seguridad de Githup no dejo subir 

def generate_plan(user_id, method):
    """
    Genera un plan de mejora y diagnóstico usando tres APIs (Google Generative AI, Llama API, OpenAI).
    :param user_id: ID del usuario.
    :param method: Método de evaluación (ROSA, NIOSH, OWAS, REBA).
    :return: Diccionario con el diagnóstico y plan de mejora de cada API.
    """
    user = User.query.get(user_id)
    if not user:
        return {"error": "Usuario no encontrado"}

    # Crear el prompt basado en el método
    prompt = ""
    if method == "ROSA":
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
    elif method == "OWAS":
        owas_score = OwasScore.query.filter_by(user_id=user_id).order_by(OwasScore.evaluation_date.desc()).first()
        if not owas_score:
            return {"error": "No se encontraron resultados para el método OWAS"}

        prompt = (
            f"Usuario: {user.username}\n"
            f"Puntajes OWAS:\n"
            f"- Puntaje de espalda: {owas_score.back_score}\n"
            f"- Puntaje de brazos: {owas_score.arms_score}\n"
            f"- Puntaje de piernas: {owas_score.legs_score}\n"
            f"- Puntaje total: {owas_score.total_score}\n\n"
            f"Con base en estos resultados, genera un diagnóstico y un plan de mejora ergonómico detallado."
        )
    elif method == "REBA":
        reba_score = RebaScore.query.filter_by(user_id=user_id).order_by(RebaScore.evaluation_date.desc()).first()
        if not reba_score:
            return {"error": "No se encontraron resultados para el método REBA"}

        prompt = (
            f"Usuario: {user.username}\n"
            f"Puntajes REBA:\n"
            f"- Grupo A: {reba_score.group_a_score}\n"
            f"- Grupo B: {reba_score.group_b_score}\n"
            f"- Puntaje total: {reba_score.total_score}\n\n"
            f"Con base en estos resultados, genera un diagnóstico y un plan de mejora ergonómico detallado."
        )
    else:
        return {"error": "Método no soportado"}

    # Obtener respuestas de las tres APIs
    results = {}

    # Google Generative AI
    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        results["google"] = response.text
    except Exception as e:
        results["google"] = f"Error: {str(e)}"

    # Llama API
    try:
        llama_request = {
            "model": "llama3.1-70b",
            "messages": [{"role": "user", "content": prompt}]
        }
        llama_response = llama.run(llama_request)
        llama_content = llama_response.json()
        results["llama"] = llama_content['choices'][0]['message']['content']
    except Exception as e:
        results["llama"] = f"Error: {str(e)}"

    # OpenAI
    try:
        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        results["openai"] = openai_response.choices[0].message['content']
    except Exception as e:
        results["openai"] = f"Error: {str(e)}"

    return {"diagnostic_plan": results}