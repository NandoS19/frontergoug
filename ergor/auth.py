from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from ergor.models import User
from ergor import db
import os

bp = Blueprint('auth', __name__, url_prefix='/auth') 

@bp.route('/register', methods=('POST', 'GET'))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')
        height = request.form.get('height')
        weight = request.form.get('weight')
        gender = request.form.get('gender')
        hours = request.form.get('hours')
        job_title = request.form.get('job_title')
        
        user = User(username, email, generate_password_hash(password), age=age, height=height, weight=weight,gender=gender, hours=hours, job_title=job_title)
        
        #Validacion de datos
        error = None
        #Comparando nombre de usuario con los existentes
        user_email = User.query.filter_by(email=email).first()
        
        if user_email is not None:
            error = 'El correo ya está registrado'
        else:
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        flash(error)
        
    return render_template('auth/register.html')

@bp.route('/login', methods=('POST', 'GET'))
def login():
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        #Validacion de datos
        error = None
        user = User.query.filter_by(email=email).first()
        
        if user is None:
            error = 'Correo o contraseña incorrectos'
        elif not check_password_hash(user.password, password):
            error = 'Correo o contraseña incorrectos'
        if error is None:
            session.clear()
            session['user_id'] = user.user_id
            return redirect(url_for('home.index'))
        flash(error)
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)
        
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.index'))

import functools
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

#Editar perfil
from werkzeug.utils import secure_filename

@bp.route('/profile/<int:id>', methods=('POST', 'GET'))
@login_required
def profile(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        password = request.form.get('password')
        db.session.commit()
        
        error = None
        if len(password) != 0:
            user.password = generate_password_hash(password)
        elif len(password) > 0 and len(password) < 8:
            error = 'La contraseña debe tener al menos 8 caracteres'
            
        if request.files['photo']:
            photo = request.files['photo']
            filename = secure_filename(photo.filename)
            photo.save(f'ergor/static/media/{filename}')
            user.photo = f'media/{filename}'    
            
        if error is None:
            db.session.commit()
            return redirect(url_for('auth.profile', id=user.user_id))
        else:
            flash(error)
            
        flash(error)
    return render_template('auth/profile.html', user=user)

# Ruta para subir videos
@bp.route('/upload/<int:id>', methods=('GET', 'POST'))
@login_required
def upload(id):
    
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
       error = None
       
       if 'uploadVideo' not in request.files:
           
           error = 'No se ha seleccionado un archivo'
           flash(error)
           
       else:
            # Obtener el archivo del formulario
            video_path = request.files['uploadVideo']
            # Obtener el valor del combo box
            metodo = request.form.get('metodo')
            
            if video_path.filename == '':
                error = 'No se ha seleccionado un archivo'
                flash(error)
            
            if video_path and allowed_file(video_path.filename):
                
                # Guardar el archivo en la carpeta definida
                filename = secure_filename(video_path.filename)
                filepath = os.path.join('ergor', 'static', 'uploads', filename)
                video_path.save(filepath)

                # Guardar la ruta del archivo en la base de datos
                user.video_path = os.path.join('uploads', filename)

                if error is None:
                    db.session.commit()
                    flash('Video subido con éxito')
                    # Redirigir a la función correspondiente según el método de evaluación
                    if metodo == 'ROSA':
                        return redirect(url_for('evaluate.rosa', id=user.user_id))
                    elif metodo == 'REBA':
                        return redirect(url_for('evaluate.reba', id=user.user_id))
                    elif metodo == 'OWAS':
                        return redirect(url_for('evaluate.owas', id=user.user_id))
                    elif metodo == 'NIOSH':
                        return redirect(url_for('evaluate.niosh', id=user.user_id))
                    else:
                        flash('Método de evaluación no válido')
                else:
                    flash(error)
            else:
                error = 'Formato de archivo no permitido'
                flash(error)
    
    return render_template('admin/uploadvideo.html', user=user)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS