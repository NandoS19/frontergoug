from flask import Blueprint, render_template, request, redirect, url_for, flash,g, session, jsonify
from .auth import login_required
from ergor import db
from ergor.models import User, RosaScore, OwasScore, NioshScore
import os

# Importar la función para generar planes de mejora
from ergor.generate_plan import generate_plan

bp = Blueprint('evaluate', __name__, url_prefix='/evaluate') 

@bp.route('/evaluate')
@login_required
def evaluate_page():
    
    return f'Pagina de evaluacion'

@bp.route('/results/<int:id>', methods=['GET'])
@login_required
def results(id):
    user = User.query.get_or_404(id)
    return render_template('admin/results.html', user=user)

@bp.route('/rosa/<int:id>', methods=['GET'])
def rosa(id):
    # Lógica para procesar el video con el método ROSA
    
    user = User.query.get_or_404(id)
    
    if not user.video_path:
        flash('El usuario no tiene un video subido')
        return redirect(url_for('auth.upload', id = user.user_id))
    
    filepath = os.path.join('ergor', 'static', user.video_path)
    #flash (f"El archivo es: {filepath}")
    
    # Importar los módulos para procesamiento y evaluación
    from ergor.process_videoROSA import process_video
    from ergor.rosa_evaluation import evaluate_rosa

    # Procesar el video para calcular ángulos
    try:
        angles = process_video(filepath)
        #flash(f"Ángulos calculados: {angles}")
    except Exception as e:
        flash(f"Error al procesar el video: {str(e)}")
        return redirect(url_for('auth.upload', id=user.user_id))

    # Calcular puntajes ROSA
    try:
        scores = evaluate_rosa(angles)

        # Guardar los resultados en la base de datos
        rosa_score = RosaScore(
            user_id=user.user_id,
            chair_score=scores["chair_score"],
            monitor_score=scores["monitor_score"],
            phone_score=scores["phone_score"],
            keyboard_score=scores["keyboard_score"],
            total_score=scores["total_score"]
        )
        db.session.add(rosa_score)
        db.session.commit()

        flash("Evaluación ROSA completada con éxito")
        return render_template('admin/rosa.html', user=user, scores=scores)
    except Exception as e:
        flash(f"Error al calcular los puntajes ROSA: {str(e)}")
        return redirect(url_for('auth.upload', id=user.user_id))
# Ruta para generar el plan de mejora del método ROSA
@bp.route('/rosa/<int:id>/plan', methods=['GET'])
def rosa_plan(id):
    result = generate_plan(user_id=id, method="ROSA")
    if "error" in result:
        flash(result["error"])
        return redirect(url_for('evaluate.rosa', id=id))

    return render_template('admin/plan.html', user_id=id, method="ROSA", plan=result["diagnostic_plan"])

@bp.route('/reba/<int:id>', methods=['GET'])
def reba(id):
    # Lógica para procesar el video con el método REBA
    return f'Lógica para procesar el video con el método REBA'
    #return render_template('evaluate/reba.html', id=id)

@bp.route('/owas/<int:id>', methods=['GET'])
def owas(id):
    # Lógica para procesar el video con el método OWAS
 
    user = User.query.get_or_404(id)
    
    if not user.video_path:
        flash('El usuario no tiene un video subido')
        return redirect(url_for('auth.upload', id=user.user_id))
    
    filepath = os.path.join('ergor', 'static', user.video_path)
    
    # Importar los módulos para procesamiento y evaluación
    from ergor.process_videoOWAS import process_video_owas
    from ergor.owas_evaluation import evaluate_owas
    
    # Procesar el video para calcular ángulos
    try:
        angles = process_video_owas(filepath)
    except Exception as e:
        flash(f"Error al procesar el video: {str(e)}")
        return redirect(url_for('auth.upload', id=user.user_id))
    
    # Guardar los resultados en la base de datos
    try:
        
        scores = evaluate_owas(angles)
        
        owas_scores = OwasScore(
            user_id=user.user_id,
            back_score=scores["back_score"],
            arms_score=scores["arms_score"],
            legs_score=scores["legs_score"],
            total_score=scores["total_score"],
        )
        
        db.session.add(owas_scores)
        db.session.commit()
        
        flash("Evaluación OWAS completada con éxito")
        return render_template('admin/owas.html', user=user, scores=scores)
    except Exception as e:
        flash(f"Error al calcular los puntajes OWAS: {str(e)}")
        return redirect(url_for('auth.upload', id=user.user_id))

@bp.route('/niosh/<int:id>', methods=['GET'])
def niosh(id):
    from ergor.process_videoNIOSH import process_video
    from ergor.niosh_evaluation import evaluate_niosh

    user = User.query.get_or_404(id)

    if not user.video_path:
        flash('El usuario no tiene un video subido')
        return redirect(url_for('auth.upload', id=user.user_id))

    filepath = os.path.join('ergor', 'static', user.video_path)

    try:
        # Procesar el video para calcular factores
        factors = process_video(filepath)
    except Exception as e:
        flash(f"Error al procesar el video: {str(e)}")
        return redirect(url_for('auth.upload', id=user.user_id))

    try:
        # Calcular RWL y LI
        load_weight = 10  # Ejemplo: peso de la carga (kg)
        frequency = 15  # Ejemplo: frecuencia de levantamiento
        scores = evaluate_niosh(
            load_weight,
            factors["horizontal_distance"],
            factors["vertical_distance"],
            factors["asymmetry_angle"],
            frequency
        )

        # Guardar en la base de datos
        niosh_score = NioshScore(
            user_id=user.user_id,
            load_weight=load_weight,
            horizontal_distance=factors["horizontal_distance"],
            vertical_distance=factors["vertical_distance"],
            asymmetry_angle=factors["asymmetry_angle"],
            frequency=frequency,
            rwl=scores["RWL"]
        )
        db.session.add(niosh_score)
        db.session.commit()

        flash("Evaluación NIOSH completada con éxito")
        return render_template(
            'admin/niosh.html',
            user=user,
            scores=scores
        )
    except Exception as e:
        flash(f"Error al calcular los puntajes NIOSH: {str(e)}")
        return redirect(url_for('auth.upload', id=user.user_id))
# Ruta para generar el plan de mejora del método NIOSH
@bp.route('/niosh/<int:id>/plan', methods=['GET'])
def niosh_plan(id):
    result = generate_plan(user_id=id, method="NIOSH")
    if "error" in result:
        flash(result["error"])
        return redirect(url_for('evaluate.niosh', id=id))

    return render_template('admin/plan.html', user_id=id, method="NIOSH", plan=result["diagnostic_plan"])