from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from ergor.models import User, Employe
from ergor import db
import os
import re

bp = Blueprint('auth', __name__, url_prefix='/auth') 

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bp.route('/register', methods=('POST', 'GET'))
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        #Validacion de datos
        error = None
        
        # Validaciones de formato
        if not re.match("^[a-zA-Z0-9]+$", username):
            error = 'El nombre de usuario solo puede contener caracteres alfanuméricos'
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error = 'El correo electrónico no es válido'
        elif len(password) < 8:
            error = 'La contraseña debe tener al menos 8 caracteres'
        
        #Comparando nombre de usuario con los existentes
        user_email = User.query.filter_by(email=email).first()
        
        if user_email is not None:
            error = 'El correo ya está registrado'
        else:
            user = User(username, email, generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        flash(error)
        
    return render_template('auth/register.html')

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get_or_404(user_id)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home.index'))

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import functools
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Ruta para subir videos
@bp.route('/upload/<int:id>', methods=('GET', 'POST'))
@login_required
def upload(id):
    
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        
        # Obtener los datos del formulario
        form_data = request.form
        required_fields = ['name', 'last_name', 'work', 'time_company', 'job_title', 
                           'age', 'height', 'weight', 'gender', 'hours']
        error = None

        # Validar campos obligatorios
        for field in required_fields:
            if not form_data.get(field):
                error = f"El campo {field} es obligatorio"
                break
       
       
      # Validar formato de campos específicos
        if error is None:
            if not re.match("^[a-zA-Z]+$", form_data['name']):
                error = 'El nombre solo puede contener letras'
            elif not re.match("^[a-zA-Z]+$", form_data['last_name']):
                error = 'El apellido solo puede contener letras'

        if error:
            flash(error)
            return redirect(url_for('auth.upload', id=user.user_id))

        # Crear empleado
        employee = Employe(
            name=form_data['name'],
            last_name=form_data['last_name'],
            work=form_data['work'],
            time_company=form_data['time_company'],
            job_title=form_data['job_title'],
            age=int(form_data['age']),
            height=float(form_data['height']),
            weight=float(form_data['weight']),
            gender=form_data['gender'],
            hours=int(form_data['hours']),
            user_id=user.user_id
        )
        db.session.add(employee)
       
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
                 # user.video_path = os.path.join('uploads', filename)
                 employee.video_path = os.path.join('uploads', filename)

                 if error is None:
                     db.session.commit()
                     flash('Video subido con éxito')
                     # Redirigir a la función correspondiente según el método de evaluación
                     if metodo == 'ROSA':
                         # return redirect(url_for('evaluate.rosa', user_id=user.user_id))
                         return redirect(url_for('evaluate.rosa', user_id=user.user_id, employee_id=employee.employe_id))
                     elif metodo == 'REBA':
                         # return redirect(url_for('evaluate.reba', id=user.user_id))
                         return redirect(url_for('evaluate.reba', user_id=user.user_id, employee_id=employee.employe_id))
                     elif metodo == 'OWAS':
                         # return redirect(url_for('evaluate.owas', id=user.user_id))
                         return redirect(url_for('evaluate.owas', user_id=user.user_id, employee_id=employee.employe_id))
                     elif metodo == 'NIOSH':
                         # return redirect(url_for('evaluate.niosh', id=user.user_id))
                         return redirect(url_for('evaluate.niosh', user_id=user.user_id, employee_id=employee.employe_id))
                     else:
                         flash('Método de evaluación no válido')
                 else:
                     flash(error)
             else:
                 error = 'Formato de archivo no permitido'
                 flash(error)
    
    return render_template('admin/uploadvideo.html', user=user)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS