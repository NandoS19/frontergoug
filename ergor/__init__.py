from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    #Crear aplicacion de flask
    app = Flask(__name__)

    #Configuracion de la aplicacion
    app.config.from_object('config.Config')
    db.init_app(app)
    
    #import locale
    #locale.setlocale(locale.LC_ALL, 'es_ES')
    
    #Registrar vistas
    from ergor import home
    app.register_blueprint(home.bp)
    
    from ergor import auth
    app.register_blueprint(auth.bp)
    
    from ergor import evaluate
    app.register_blueprint(evaluate.bp)
    
    
    #Migrar modelos a base de datos
    from .models import User, RiskLevel, RebaScore, RosaScore, OwasScore, NioshScore, ImprovementPlan
    with app.app_context():
        db.create_all()

    return app