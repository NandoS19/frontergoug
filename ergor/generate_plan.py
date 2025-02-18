import os
from dotenv import load_dotenv
import google.generativeai as genai
from llamaapi import LlamaAPI
import openai
from ergor.models import User, RosaScore, NioshScore, OwasScore, RebaScore, Employe, RiskLevel
from ergor import db

# Cargar las variables de entorno
load_dotenv()

# Configurar las APIs usando variables de entorno
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llama = LlamaAPI(os.getenv("LLAMA_API_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")

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

        # Recuperar el RiskLevel relacionado con el RosaScore
        risk_level = RiskLevel.query.get(rosa_score.level_id)
        if not risk_level:
            return {"error": "No se encontró el nivel de riesgo asociado al puntaje ROSA"}
        
        prompt = (
            f"**Datos del Empleado**:\n"
            f"**Caso de estudio: Evaluación ergonómica basada en el método ROSA**\n\n"
            f"**Contexto del empleado:**\n"
            f"El empleado, {employee.name} {employee.last_name}, tiene {employee.age} años y trabaja en el sector de {employee.work} desempeñando el puesto de {employee.job_title}. \n"
            f"Lleva {employee.time_company} años trabajando en la empresa y realiza jornadas laborales de {employee.hours} horas al día.\n"
            f"Sus características físicas son las siguientes: {employee.height} m de altura y {employee.weight} kg de peso. El empleado se identifica como {employee.gender}.\n\n"
            
            f"**Resultados del análisis ergonómico:**\n"
            f"El método ROSA ha evaluado el entorno laboral del empleado, obteniendo los siguientes puntajes:\n"
            f"- Puntaje de silla: {rosa_score.chair_score}.\n"
            f"- Puntaje de monitor: {rosa_score.monitor_score}.\n"
            f"- Puntaje de teclado: {rosa_score.keyboard_score}.\n"
            f"- Puntaje de ratón: {rosa_score.mouse_score}.\n"
            f"- Puntaje de teléfono: {rosa_score.phone_score}.\n"
            f"- Puntaje total ROSA: {rosa_score.total_score}.\n\n"
            
            f"**Nivel de Riesgo:**\n"
            f"- Puntuación de riesgo: {risk_level.risk_score}\n"
            f"- Nivel de riesgo: {risk_level.risk}\n"
            f"- Descripción: {risk_level.description}\n\n"
            
            f"**Solicitudes:**\n"
            f"Con base en los datos proporcionados, realiza las siguientes tareas:\n"
            f"1. **Diagnóstico detallado:** Identifica las principales áreas de riesgo ergonómico relacionadas con los resultados del método ROSA. Describe cómo cada puntaje impacta en la salud del empleado y justifica por qué se consideran riesgos críticos.\n"
            f"2. **Plan de mejora ergonómico personalizado:** Proporciona recomendaciones claras y prácticas para abordar los riesgos identificados. Asegúrate de incluir soluciones específicas, como ajustes en el mobiliario, cambios en el diseño del entorno laboral, prácticas preventivas y sugerencias de capacitación ergonómica.\n"
            f"3. **Justificación del plan:** Explica brevemente por qué las soluciones propuestas son efectivas para mitigar los riesgos y cómo contribuyen al bienestar del empleado.\n\n"
            f"**Notas adicionales:**\n"
            f"- El diagnóstico debe ser lo más detallado posible, priorizando las áreas con mayor puntaje.\n"
            f"- Las recomendaciones deben ser prácticas, priorizando aquellas de fácil implementación pero con alto impacto.\n"
            f"- Considera el perfil físico del empleado y el contexto laboral para personalizar las soluciones."
            f"- La respuesta debe ser devuelta como si fueras a llenar una ficha medica."
        )
    
    elif method == "NIOSH":
        niosh_score = NioshScore.query.filter_by(employe_id=employee_id).order_by(NioshScore.evaluation_date.desc()).first()
        if not niosh_score:
            return {"error": "No se encontraron resultados para el método NIOSH"}

        prompt = (
            f"-solo con los datos que te estoy dando aqui, excepto en diagnostico y pan de mejora, en eso si dame mas detalles de un diagnostico y plan de mejora ergonomica, pero manten la estructura de FICHA MÉDICA ERGONÓMICA, Datos del Empleado, Método de Evaluación: NIOSH , este mensaje no muestres de (solo con los datos que te estoy dando aqui):"
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
            f"- Índice de Levantamiento (LI): {niosh_score.li}\n"
            
            
            f"**Diagnóstico**:\n"
            f"Se ha detectado que el empleado está expuesto a un riesgo elevado de lesiones en la columna debido al índice de levantamiento (LI) y peso de la carga.\n\n"
            
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
            f"**Datos del Empleado**:\n"
            f"**Caso de estudio: Evaluación ergonómica basada en el método OWAS**\n\n"
            f"**Contexto del empleado:**\n"
            f"- Nombre: {employee.name} {employee.last_name}\n"
            f"- Puesto de Trabajo: {employee.job_title}\n"
            f"- Edad: {employee.age} años\n"
            f"- Altura: {employee.height} m\n"
            f"- Peso: {employee.weight} kg\n"
            f"- Género: {employee.gender}\n"
            f"- Horas de trabajo por día: {employee.hours} horas\n\n"
            
            f"El método OWAS ha evaluado el entorno laboral del empleado, obteniendo los siguientes puntajes:\n"
            f"- Puntaje de espalda: {owas_score.back_category}\n"
            f"- Puntaje de brazos: {owas_score.arms_category}\n"
            f"- Puntaje de piernas: {owas_score.legs_category}\n"
            f"- Puntaje de carga: {owas_score.load_weight}\n\n"
            f"- Puntaje de categoria: {owas_score.action_category}\n\n"
            
            f"**Diagnóstico**:\n"
            f"La postura durante el trabajo genera riesgos en la columna debido a las malas posiciones de espalda y brazos.\n\n"
            
            f"**Solicitudes:**\n"
            f"Con base en los datos proporcionados, realiza las siguientes tareas:\n"
            f"1. **Diagnóstico detallado:** Identifica las principales áreas de riesgo ergonómico relacionadas con los resultados del método OWAS. Describe cómo cada puntaje impacta en la salud del empleado y justifica por qué se consideran riesgos críticos.\n"
            f"2. **Plan de mejora ergonómico personalizado:** Proporciona recomendaciones claras y prácticas para abordar los riesgos identificados. Asegúrate de incluir soluciones específicas, como prácticas preventivas y sugerencias de capacitación ergonómica.\n"
            f"3. **Justificación del plan:** Explica brevemente por qué las soluciones propuestas son efectivas para mitigar los riesgos y cómo contribuyen al bienestar del empleado.\n\n"
            f"**Notas adicionales:**\n"
            f"- El diagnóstico debe ser lo más detallado posible, priorizando las áreas con mayor puntaje.\n"
            f"- Las recomendaciones deben ser prácticas, priorizando aquellas de fácil implementación pero con alto impacto.\n"
            f"- Considera el perfil físico del empleado y el contexto laboral para personalizar las soluciones."
            f"- La respuesta debe ser devuelta como si fueras a llenar una ficha medica."
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
            f"**Puntaje del tronco:{reba_score.trunk_score}**\n"
            f"**Puntaje del cuello:{reba_score.neck_score}**\n"
            f"**Puntaje de las piernas:{reba_score.leg_score}**\n"
            f"**Puntaje del brazo:{reba_score.arm_score}**\n"
            f"**Puntaje del antebrazo:{reba_score.forearm_score}**\n"
            f"**Puntaje de la muñeca:{reba_score.wrist_score}**\n"
            f"**Grupo A:{reba_score.group_a_score}**\n"
            f"**Grupo B:{reba_score.group_b_score}**\n"
            f"- Puntaje total: {reba_score.total_score}\n"
            
            f"**Diagnóstico**:\n"
            f"El análisis de las posturas en las tareas de estiba indica una carga ergonómica significativa, con especial impacto en la espalda, hombros y extremidades superiores. Los valores obtenidos a través del método REBA reflejan los riesgos asociados a la manipulación manual de cargas y las posturas forzadas adoptadas durante la jornada laboral.\n\n"
            f"Los resultados se presentan a continuación:\n"
            f"- **Grupo A**: Puntaje total {reba_score.group_a_score}.\n"
            f"- **Grupo B**: Puntaje total {reba_score.group_b_score}.\n"
            f"- **Puntaje Total REBA**: {reba_score.total_score}.\n\n"
            f"Los valores han sido obtenidos conforme a las tablas de puntuación del método REBA, garantizando un análisis ergonómico preciso.\n\n"

            f"**Plan de Mejora Ergonómica**:\n"
            f"1. Implementar técnicas de levantamiento seguro para minimizar la carga en la espalda.\n"
            f"2. Optimizar la disposición de la carga para reducir la necesidad de torsiones y flexiones excesivas.\n"
            f"3. Introducir equipos auxiliares, como fajas ergonómicas o dispositivos de asistencia en la manipulación de peso.\n"
            f"4. Establecer pausas programadas con ejercicios de estiramiento para aliviar la fatiga muscular.\n"
            f"5. Capacitar a los estibadores en prácticas ergonómicas adecuadas para prevenir lesiones musculoesqueléticas.\n"

            


        )

    # Obtener respuestas de las tres APIs
    results = {}

    # Google Generative AI
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
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


