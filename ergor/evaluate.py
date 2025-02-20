from flask import Blueprint, render_template, request, redirect, url_for, flash,g, session, jsonify
from .auth import login_required
from ergor import db
from ergor.models import User, RosaScore, OwasScore, NioshScore, RebaScore, Employe, RiskLevel
import os

# Importar la función para generar planes de mejora
from ergor.generate_plan import generate_plan

bp = Blueprint('evaluate', __name__, url_prefix='/evaluate') 

@bp.route('/rosa/<int:user_id>/<int:employee_id>', methods=['GET'])
@login_required
def rosa(user_id,employee_id):
    # Lógica para procesar el video con el método ROSA
    
    user = User.query.get_or_404(user_id)
    employe = Employe.query.get_or_404(employee_id)
    
    if not employe.video_path:
        flash('El empleado no tiene un video subido')
        return redirect(url_for('auth.upload', id = user.user_id))
    
    filepath = os.path.join('ergor', 'static', employe.video_path)
    print (f"El archivo es: {filepath}")
    #flash (f"El archivo es: {filepath}")
    
    # Importar los módulos para procesamiento y evaluación
    # from ergor.process_videoROSA import process_video
    from ergor.controller.rosa_evaluation import evaluate_ROSA
    from ergor.controller.rosaVideo import process_video

    # Procesar el video para calcular ángulos
    try:
        angles = process_video(filepath)
        print (f"Los ángulos calculados son: {angles}")
        #flash(f"Ángulos calculados: {angles}")
    except Exception as e:
        flash(f"Error al procesar el video: {str(e)}")
        print (f"Error al procesar el video: {str(e)}")
        return redirect(url_for('auth.upload', id=user.user_id))

    # Calcular puntajes ROSA
    try:
        scores = evaluate_ROSA(angles, None)
        
        # Determinar el nivel de riesgo
        risk_level_info = scores["risk_level_info"]

        # Guardar el nivel de riesgo en la tabla RiskLevel
        risk_level = RiskLevel(
            risk_score=scores["total_score"],
            risk=risk_level_info["risk"],
            risk_level=risk_level_info["risk_level"],
            description=risk_level_info["description"]
        )
        db.session.add(risk_level)
        db.session.commit()

        # Guardar los resultados en la base de datos
        rosa_score = RosaScore(
            employe_id=employe.employe_id,
            chair_score=scores["chair_score"],
            monitor_score=scores["monitor_score"],
            phone_score=scores["phone_score"],
            keyboard_score=scores["keyboard_score"],
            mouse_score=scores["mouse_score"],
            total_score=scores["total_score"],
            level_id=risk_level_info["risk_level"]
        )
        db.session.add(rosa_score)
        db.session.commit()

        #flash("Evaluación ROSA completada con éxito")
        print (f"Evaluación ROSA completada con éxito")
        print (f"Los puntajes ROSA son: {scores}")
        return render_template('admin/rosa.html', user=user, employe=employe, scores=scores,
                            suma_altura_profundidad=scores["suma_altura_profundidad"],
                            suma_reposabrazos_respaldo=scores["suma_reposabrazos_respaldo"],
                            monitor_phone_score=scores["monitor_phone_score"],
                            keyboard_mouse_score=scores["keyboard_mouse_score"],
                            peripherals_score=scores["peripherals_score"])
    except Exception as e:
        flash(f"Error al calcular los puntajes ROSA: {str(e)}")
        print (f"Error al calcular los puntajes ROSA: {str(e)}")
        return redirect(url_for('auth.upload',  id=user.user_id))
    
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Ruta para generar el plan de mejora del método ROSA
@bp.route('/rosa/<int:user_id>/<int:employee_id>/plan', methods=['GET'])
@login_required
def rosa_plan(user_id, employee_id):
    result = generate_plan(user_id=user_id, employee_id=employee_id, method="ROSA")
    if "error" in result:
        flash(result["error"])
        return redirect(url_for('evaluate.rosa', id=id))

    return render_template('admin/plan.html',user_id=user_id, employee_id=employee_id, method="ROSA", plan=result["diagnostic_plan"])

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bp.route('/reba/<int:user_id>/<int:employee_id>', methods=['GET'])
@login_required
def reba(user_id,employee_id):

    user = User.query.get_or_404(user_id)
    employe = Employe.query.get_or_404(employee_id)
    
    if not employe.video_path:
        flash('El usuario no tiene un video subido.')
        return redirect(url_for('auth.upload', id=user.user_id))
    
    filepath = os.path.join('ergor', 'static', employe.video_path)
    print (f"El archivo es: {filepath}")

    # Importar las funciones necesarias para procesar el video
    from ergor.controller.process_videoREBA import process_video
    from ergor.controller.process_videoREBA import calcular_puntuacion_global_A
    from ergor.controller.process_videoREBA import calcular_puntuacion_global_grupo_B
    from ergor.controller.process_videoREBA import calcular_puntuacion_final

    try:
        # Procesamos el video y obtenemos los datos de los códigos posturales más altos
        print("Procesando video:", filepath)
        highest_postural_codes = process_video(filepath)
        print("Códigos posturales obtenidos:", highest_postural_codes)

        # Validar que todos los valores sean válidos
        if not highest_postural_codes or any(value is None for value in highest_postural_codes.values()):
            raise ValueError("Códigos posturales no válidos o incompletos.")
        
        # Renombrar claves para coincidir con las columnas de la tabla
        formatted_codes = {
            "trunk_score": highest_postural_codes["espalda"],
            "neck_score": highest_postural_codes["cuello"],
            "leg_score": highest_postural_codes["piernas"],
            "arm_score": highest_postural_codes["brazos"],
            "forearm_score": highest_postural_codes["antebrazos"],
            "wrist_score": highest_postural_codes["muñeca"]
        }
        print("Códigos formateados:", formatted_codes)
        
        # Calcular las puntuaciones globales del Grupo A y Grupo B
        puntuacion_grupo_A = calcular_puntuacion_global_A(
            formatted_codes["trunk_score"], 
            formatted_codes["neck_score"], 
            formatted_codes["leg_score"]
        )
        
        puntuacion_grupo_B = calcular_puntuacion_global_grupo_B(
            formatted_codes["arm_score"], 
            formatted_codes["forearm_score"], 
            formatted_codes["wrist_score"]
        )
        
        puntuacion_final = calcular_puntuacion_final(puntuacion_grupo_A, puntuacion_grupo_B)
        
        # Determinar el nivel de riesgo basado en la puntuación final
        if puntuacion_final <= 3:
            risk_level = "Bajo"
        elif puntuacion_final <= 6:
            risk_level = "Moderado"
        else:
            risk_level = "Alto"
        
        # Guardamos los códigos posturales y las puntuaciones en la base de datos
        from ergor.models import RebaScore
        reba_score = RebaScore(
            employe_id=employe.employe_id,
            trunk_score=formatted_codes["trunk_score"],
            neck_score=formatted_codes["neck_score"],
            leg_score=formatted_codes["leg_score"],
            arm_score=formatted_codes["arm_score"],
            forearm_score=formatted_codes["forearm_score"],
            wrist_score=formatted_codes["wrist_score"],
            group_a_score=puntuacion_grupo_A,
            group_b_score=puntuacion_grupo_B,
            total_score=puntuacion_final
        )
        db.session.add(reba_score)
        db.session.commit()
        
        # Mensaje de éxito
        flash("Evaluación REBA completada con éxito.")
        
        # Renderizar la página de resultados
        return render_template('admin/reba.html', 
                                user=user,
                                employe=employe, 
                                group_a_codes=formatted_codes,
                                group_b_codes=formatted_codes,
                                puntuacion_grupo_A=puntuacion_grupo_A,
                                puntuacion_grupo_B=puntuacion_grupo_B,
                                puntuacion_final=puntuacion_final,
                                risk_level=risk_level)

    except Exception as e:
        # Capturamos cualquier excepción y mostramos un mensaje de error
        flash(f'Ocurrió un error al procesar el video: {str(e)}')
        print(f"Error procesando video: {str(e)}")
        
        # Redirigir a la página de carga de video
        return redirect(url_for('auth.upload', id=user.user_id))

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bp.route('/reba/<int:user_id>/<int:employee_id>/plan', methods=['GET'])
@login_required
def reba_plan(user_id, employee_id):
    # Genera el plan usando el método REBA
    result = generate_plan(user_id=user_id, employee_id=employee_id, method="REBA")
    
    # Verifica si hubo un error en la generación del plan
    if "error" in result:
        flash(result["error"])
        return redirect(url_for('evaluate.reba', id=id))  # Redirige a la página de evaluación REBA

    # Renderiza el plan en la plantilla correspondiente
    return render_template('admin/plan.html', user_id=user_id, employee_id=employee_id, method="REBA", plan=result["diagnostic_plan"])

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bp.route('/owas/<int:user_id>/<int:employee_id>', methods=['GET'])
@login_required
def owas(user_id, employee_id):
    # Lógica para procesar el video con el método OWAS
 
    user = User.query.get_or_404(user_id)
    employe = Employe.query.get_or_404(employee_id)

    if not employe.video_path:
        flash('El usuario no tiene un video subido')
        return redirect(url_for('auth.upload', id=user.user_id))
    
    filepath = os.path.join('ergor', 'static', employe.video_path)
    print (f"El archivo es: {filepath}")
    #flash (f"El archivo es: {filepath}")
    
    # Importar los módulos para procesamiento y evaluación
    from ergor.controller.process_videoOWAS import process_video
    from ergor.controller.owas_evaluation import evaluate_owas
    
    # Procesar el video para calcular ángulos
    try:
        angles = process_video(filepath)
        load_weight = employe.weight
        scores = evaluate_owas(angles, load_weight=load_weight)
        
        owas_scores = OwasScore(
            employe_id=employe.employe_id,
            back_category=scores["back_category"],
            arms_category=scores["arms_category"],
            legs_category=scores["legs_category"],
            load_category=scores["load_category"],
            action_category=scores["action_category"],
            load_weight=load_weight
        )
        
        db.session.add(owas_scores)
        db.session.commit()
        
        flash("Evaluación OWAS completada con éxito")
        print (f"Los puntajes OWAS son: {scores}")
        return render_template('admin/owas.html', user=user, employe=employe,scores=scores)
    except Exception as e:
        flash(f"Error al calcular los puntajes OWAS: {str(e)}")
        return redirect(url_for('auth.upload', id=user.user_id))

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Ruta para generar el plan de mejora del método OWAS
@bp.route('/owas/<int:user_id>/<int:employee_id>/plan', methods=['GET'])
@login_required
def owas_plan(user_id, employee_id):
    result = generate_plan(user_id=user_id, employee_id=employee_id, method="OWAS")
    if "error" in result:
        flash(result["error"])
        return redirect(url_for('evaluate.owas', id=id))

    return render_template('admin/plan.html', user_id=id, employee_id=employee_id,method="OWAS", plan=result["diagnostic_plan"])

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bp.route('/niosh/<int:user_id>/<int:employee_id>', methods=['GET'])
@login_required
def niosh(user_id,employee_id):

    user = User.query.get_or_404(user_id)
    employe = Employe.query.get_or_404(employee_id)

    from ergor.controller.process_videoNIOSH import process_video
    from ergor.controller.niosh_evaluation import evaluate_niosh

    if not employe.video_path:
        flash('El usuario no tiene un video subido.')
        return redirect(url_for('auth.upload', id=user.user_id))
    
    filepath = os.path.join('ergor', 'static', employe.video_path)

    try:
        # Procesar el video para calcular factores
        factors = process_video(filepath)
    except Exception as e:
        flash(f"Error al procesar el video: {str(e)}")
        return redirect(url_for('auth.upload', id=user.user_id))

    try:
        # Calcular RWL y LI
        load_weight = session.get('load_weight')

        if not load_weight:
            flash("No se encontró el peso de la carga ingresado. Intente nuevamente.", "error")
            print("DEBUG: session.get('load_weight'):", session.get('load_weight'))  # ✅ Depuración
            return redirect(url_for('auth.upload', id=user.user_id))

        flash(f"Peso de la carga recuperado: {load_weight}", "success")  # ✅ Mensaje de éxito
        frequency = 2     # Frecuencia de levantamiento

        # Calcular RWL y LI
        scores = evaluate_niosh(
            load_weight,
            factors["horizontal_distance"],
            factors["vertical_distance"],
            factors["asymmetry_angle"],
            frequency,
            factors["displacement_distance"],
            factors["grip_quality"]  # Derivado automáticamente por process_video
        )

        # Guardar los resultados en la base de datos
        niosh_score = NioshScore(
            employe_id=employe.employe_id,
            load_weight=load_weight,
            horizontal_distance=factors["horizontal_distance"],
            vertical_distance=factors["vertical_distance"],
            asymmetry_angle=factors["asymmetry_angle"],
            frequency=frequency,
            displacement_distance=factors["displacement_distance"],
            grip_quality=factors["grip_quality"],
            rwl=scores["RWL"],
            li=scores["LI"]  # NUEVO: Guardar LI en la base de datos
        )
        db.session.add(niosh_score)
        db.session.commit()

        # Mostrar los resultados en la plantilla
        flash("Evaluación NIOSH completada con éxito")
        return render_template(
            'admin/niosh.html',
            user=user,
            employe=employe,
            scores=scores
        )

    except Exception as e:
        flash(f"Error al calcular los puntajes NIOSH: {str(e)}")
        return redirect(url_for('auth.upload', id=user.user_id))

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Ruta para generar el plan de mejora del método NIOSH
@bp.route('/niosh/<int:user_id>/<int:employee_id>/plan', methods=['GET'])
@login_required
def niosh_plan(user_id, employee_id):
    result = generate_plan(user_id=user_id, employee_id=employee_id, method="NIOSH")
    if "error" in result:
        flash(result["error"])
        return redirect(url_for('evaluate.niosh', id=id))

    return render_template('admin/plan.html', user_id=user_id, employee_id=employee_id, method="NIOSH", plan=result["diagnostic_plan"])

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bp.route('/evaluate')
@login_required
def evaluate_page():
    
    return f'Pagina de evaluacion'

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bp.route('/results/<int:id>', methods=['GET'])
@login_required
def results(id):
    user = User.query.get_or_404(id)
    return render_template('admin/results.html', user=user)
