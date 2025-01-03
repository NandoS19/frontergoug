from flask import Blueprint, render_template, request, redirect, url_for, flash,g, session, jsonify
from .auth import login_required
from ergor import db
from ergor.models import User, RosaScore
import os

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

@bp.route('/reba/<int:id>', methods=['GET'])
def reba(id):
    # Lógica para procesar el video con el método REBA
    return f'Lógica para procesar el video con el método REBA'
    #return render_template('evaluate/reba.html', id=id)

@bp.route('/owas/<int:id>', methods=['GET'])
def owas(id):
    # Lógica para procesar el video con el método OWAS
    return f'Lógica para procesar el video con el método OWAS'
    #return render_template('evaluate/owas.html', id=id)

@bp.route('/niosh/<int:id>', methods=['GET'])
def niosh(id):
    # Lógica para procesar el video con el método NIOSH
    return f'Lógica para procesar el video con el método NIOSH'
    #return render_template('evaluate/niosh.html', id=id)