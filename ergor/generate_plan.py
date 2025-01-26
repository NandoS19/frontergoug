import google.generativeai as genai
from llamaapi import LlamaAPI
import openai
from ergor.models import User, RosaScore, NioshScore, OwasScore, RebaScore, Employe
from ergor import db

# Configurar las APIs
genai.configure(api_key="AIzaSyAo46Co2yniw1aQDFWbcZsfsVipbv0v_zM")  # API de Google Generative AI
llama = LlamaAPI("LA-05ca3abe055d4847aebd6b034374da2ff5a07974966e418e9d7f72b18635c32b")  # Llama API
#llave de api openai falta aqui, por motivo de seguridad de Githup no dejo subir 


def generate_plan(user_id, employee_id, method):
    """
    Genera un plan de mejora y diagnóstico en formato de ficha médica usando tres APIs.
    :param user_id: ID del usuario.
    :param employee_id: ID del empleado.
    :param method: Método de evaluación (ROSA, NIOSH, OWAS, REBA).
    :return: Diccionario con el diagnóstico y plan de mejora de cada API.
    """
    user = User.query.get(user_id)
    if not user:
        return {"error": "Usuario no encontrado"}
    
    employee = Employe.query.get(employee_id)
    if not employee:
        return {"error": "Empleado no encontrado"}

    # Crear el prompt basado en el método
    prompt = ""
    if method == "ROSA":
        rosa_score = RosaScore.query.filter_by(employe_id=employee_id).order_by(RosaScore.evaluation_date.desc()).first()
        if not rosa_score:
            return {"error": "No se encontraron resultados para el método ROSA"}

        prompt = (
            f"**FICHA MÉDICA ERGONÓMICA**\n\n"
            f"**Datos del Empleado**:\n"
            f"- Nombre: {employee.name} {employee.last_name}\n"
            f"- Puesto de Trabajo: {employee.job_title}\n"
            f"- Edad: {employee.age} años\n"
            f"- Altura: {employee.height} m\n"
            f"- Peso: {employee.weight} kg\n"
            f"- Género: {employee.gender}\n"
            f"- Horas de trabajo por día: {employee.hours} horas\n\n"
            
            f"**Método de Evaluación: ROSA**\n"
            f"- Puntaje de silla: {rosa_score.chair_score}\n"
            f"- Puntaje de monitor: {rosa_score.monitor_score}\n"
            f"- Puntaje de teclado: {rosa_score.keyboard_score}\n"
            f"- Puntaje de teléfono: {rosa_score.phone_score}\n"
            f"- Puntaje total: {rosa_score.total_score}\n\n"
            
            f"**Diagnóstico**:\n"
            f"Con base en los puntajes anteriores, se observa una carga ergonómica elevada en las siguientes áreas:\n"
            f"- Silla: La posición de la silla no ofrece un soporte adecuado para {employee.name}.\n"
            f"- Monitor: El monitor está a una altura inadecuada, lo que podría generar dolor en el cuello.\n"
            f"- Teclado: El teclado está mal alineado, lo que genera tensión en los brazos y muñecas.\n\n"
            
            f"**Plan de Mejora Ergonómica**:\n"
            f"1. Ajustar la altura y el soporte de la silla para asegurar un correcto apoyo lumbar.\n"
            f"2. Colocar el monitor a la altura de los ojos para reducir la tensión en el cuello.\n"
            f"3. Reajustar la posición del teclado para mantener una postura neutral en las muñecas.\n"
            f"4. Realizar pausas activas cada 30 minutos para evitar la fatiga muscular.\n"
        )
    
    elif method == "NIOSH":
        niosh_score = NioshScore.query.filter_by(employe_id=employee_id).order_by(NioshScore.evaluation_date.desc()).first()
        if not niosh_score:
            return {"error": "No se encontraron resultados para el método NIOSH"}

        prompt = (
            f"**FICHA MÉDICA ERGONÓMICA**\n\n"
            f"**Datos del Empleado**:\n"
            f"- Nombre: {employee.name} {employee.last_name}\n"
            f"- Puesto de Trabajo: {employee.job_title}\n"
            f"- Edad: {employee.age} años\n"
            f"- Altura: {employee.height} m\n"
            f"- Peso: {employee.weight} kg\n"
            f"- Género: {employee.gender}\n"
            f"- Horas de trabajo por día: {employee.hours} horas\n\n"
            
            f"**Método de Evaluación: NIOSH**\n"
            f"- Peso de la carga: {niosh_score.load_weight} kg\n"
            f"- Distancia horizontal: {niosh_score.horizontal_distance} m\n"
            f"- Distancia vertical: {niosh_score.vertical_distance} m\n"
            f"- Ángulo de asimetría: {niosh_score.asymmetry_angle} grados\n"
            f"- Frecuencia: {niosh_score.frequency} levantamientos/minuto\n"
            f"- Desplazamiento vertical: {niosh_score.displacement_distance} m\n"
            f"- Calidad del agarre: {niosh_score.grip_quality}\n"
            f"- RWL: {niosh_score.rwl} kg\n\n"
            
            f"**Diagnóstico**:\n"
            f"Se ha detectado que el empleado está expuesto a un riesgo elevado de lesiones en la columna debido a la frecuencia y carga del trabajo.\n\n"
            
            f"**Plan de Mejora Ergonómica**:\n"
            f"1. Reducir el peso de la carga para evitar esfuerzo excesivo.\n"
            f"2. Optimizar la distancia entre el trabajador y la carga.\n"
            f"3. Asegurar una técnica adecuada de levantamiento para reducir el riesgo de lesiones.\n"
        )

    elif method == "OWAS":
        owas_score = OwasScore.query.filter_by(employe_id=employee_id).order_by(OwasScore.evaluation_date.desc()).first()
        if not owas_score:
            return {"error": "No se encontraron resultados para el método OWAS"}

        prompt = (
            f"**FICHA MÉDICA ERGONÓMICA**\n\n"
            f"**Datos del Empleado**:\n"
            f"- Nombre: {employee.name} {employee.last_name}\n"
            f"- Puesto de Trabajo: {employee.job_title}\n"
            f"- Edad: {employee.age} años\n"
            f"- Altura: {employee.height} m\n"
            f"- Peso: {employee.weight} kg\n"
            f"- Género: {employee.gender}\n"
            f"- Horas de trabajo por día: {employee.hours} horas\n\n"
            
            f"**Método de Evaluación: OWAS**\n"
            f"- Puntaje de espalda: {owas_score.back_category}\n"
            f"- Puntaje de brazos: {owas_score.arms_category}\n"
            f"- Puntaje de piernas: {owas_score.legs_category}\n"
            f"- Puntaje de carga: {owas_score.load_category}\n\n"
            f"- Puntaje de categoria: {owas_score.action_category}\n\n"
            
            f"**Diagnóstico**:\n"
            f"La postura durante el trabajo genera riesgos en la columna debido a las malas posiciones de espalda y brazos.\n\n"
            
            f"**Plan de Mejora Ergonómica**:\n"
            f"1. Proporcionar un soporte lumbar adecuado en la silla para corregir la postura de la espalda.\n"
            f"2. Reajustar la altura de los brazos y las piernas para mejorar la ergonomía.\n"
            f"3. Asegurar una correcta distribución de la carga para evitar la sobrecarga en los músculos.\n"
        )

    elif method == "REBA":
        reba_score = RebaScore.query.filter_by(employe_id=employee_id).order_by(RebaScore.evaluation_date.desc()).first()
        if not reba_score:
            return {"error": "No se encontraron resultados para el método REBA"}

        prompt = (
            f"**FICHA MÉDICA ERGONÓMICA**\n\n"
            f"**Datos del Empleado**:\n"
            f"- Nombre: {employee.name} {employee.last_name}\n"
            f"- Puesto de Trabajo: {employee.job_title}\n"
            f"- Edad: {employee.age} años\n"
            f"- Altura: {employee.height} m\n"
            f"- Peso: {employee.weight} kg\n"
            f"- Género: {employee.gender}\n"
            f"- Horas de trabajo por día: {employee.hours} horas\n\n"
            
            f"**Método de Evaluación: REBA**\n"
            f"- Puntaje total: {reba_score.total_score}\n"
            f"- Categoría: {reba_score.category}\n\n"
            
            f"**Diagnóstico**:\n"
            f"El análisis de las posturas muestra una carga ergonómica peligrosa, especialmente para la espalda y brazos.\n\n"
            
            f"**Plan de Mejora Ergonómica**:\n"
            f"1. Ajustar la postura de la espalda mediante soporte adicional en la silla.\n"
            f"2. Optimizar la altura y ángulo de trabajo para evitar posiciones forzadas.\n"
            f"3. Introducir pausas activas para reducir la tensión muscular.\n"
        )

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
            "model": "llama3.1-405b",
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
