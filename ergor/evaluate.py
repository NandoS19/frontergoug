from flask import Blueprint, render_template, request, redirect, url_for, flash,g, session, jsonify
from .auth import login_required
from ergor import db, process_video
from werkzeug.utils import secure_filename
from ergor.models import User
import os

bp = Blueprint('evaluate', __name__, url_prefix='/evaluate') 

@bp.route('/evaluate')
@login_required
def evaluate_page():
    return f'Pagina de evaluacion'

@bp.route('/results')
@login_required
def results():
    return render_template('evaluate/results.html')

