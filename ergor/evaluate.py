from flask import Blueprint, render_template, request, redirect, url_for, flash,g, session, jsonify
from .auth import login_required
from ergor import db
from ergor.models import User
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
    return f'Lógica para procesar el video con el método ROSA'
    #return render_template('evaluate/rosa.html', id=id)

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