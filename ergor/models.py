# Description: Archivo que contiene las clases de los modelos de la base de datos.
from ergor import db
from datetime import datetime
from sqlalchemy.sql import func


# Tabla de usuarios
class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(50))
    video_path = db.Column(db.String(100))
    age = db.Column(db.Integer,  nullable=True)
    height = db.Column(db.Numeric(5, 2),  nullable=True)
    weight = db.Column(db.Numeric(5, 2),  nullable=True)
    hours = db.Column(db.Numeric(2),  nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    job_title = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    last_login = db.Column(db.DateTime, nullable=True)

    reba_scores = db.relationship('RebaScore', backref='user', cascade='all, delete-orphan')
    rosa_scores = db.relationship('RosaScore', backref='user', cascade='all, delete-orphan')
    owas_scores = db.relationship('OwasScore', backref='user', cascade='all, delete-orphan')
    niosh_scores = db.relationship('NioshScore', backref='user', cascade='all, delete-orphan')
    improvement_plans = db.relationship('ImprovementPlan', backref='user', cascade='all, delete-orphan')
    
    
    def __init__(self, username, email, password, photo = None, video_path = None, age=None, height=None, weight=None, hours = None, gender=None, job_title=None):
        self.username = username
        self.email = email
        self.password = password
        self.photo = photo
        self.video_path = video_path
        self.age = age
        self.height = height
        self.weight = weight
        self.hours = hours
        self.gender = gender
        self.job_title = job_title
        
    def __repr__(self):
        return f'<User {self.username}>'
        

# Tabla de niveles de riesgo
class RiskLevel(db.Model):
    __tablename__ = 'risk_levels'
    
    level_id = db.Column(db.Integer, primary_key=True)
    risk_level = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    reba_scores = db.relationship('RebaScore', backref='risk_level', cascade='all, delete')
    rosa_scores = db.relationship('RosaScore', backref='risk_level', cascade='all, delete')
    owas_scores = db.relationship('OwasScore', backref='risk_level', cascade='all, delete')
    niosh_scores = db.relationship('NioshScore', backref='risk_level', cascade='all, delete')
    improvement_plans = db.relationship('ImprovementPlan', backref='risk_level', cascade='all, delete')
    
    def __init__(self, risk_level, description=None):
        self.risk_level = risk_level
        self.description = description
    
    def __repr__(self):
        return f'<RiskLevel {self.risk_level}>'

# Tabla de puntajes REBA
class RebaScore(db.Model):
    __tablename__ = 'reba_scores'
    
    score_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    trunk_score = db.Column(db.Integer, db.CheckConstraint('trunk_score >= 0'), nullable=False)
    neck_score = db.Column(db.Integer, db.CheckConstraint('neck_score >= 0'), nullable=False)
    leg_score = db.Column(db.Integer, db.CheckConstraint('leg_score >= 0'), nullable=False)
    arm_score = db.Column(db.Integer, db.CheckConstraint('arm_score >= 0'), nullable=False)
    forearm_score = db.Column(db.Integer, db.CheckConstraint('forearm_score >= 0'), nullable=False)
    wrist_score = db.Column(db.Integer, db.CheckConstraint('wrist_score >= 0'), nullable=False)
    evaluation_date = db.Column(db.DateTime, default=func.now())
    level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)
    
    def __init__(self, user_id, trunk_score, neck_score, leg_score, arm_score, forearm_score, wrist_score):
        self.user_id = user_id
        self.trunk_score = trunk_score
        self.neck_score = neck_score
        self.leg_score = leg_score
        self.arm_score = arm_score
        self.forearm_score = forearm_score
        self.wrist_score = wrist_score
    
    def __repr__(self):
        return f'<RebaScore {self.score_id}>'

# Tabla de puntajes ROSA
class RosaScore(db.Model):
    __tablename__ = 'rosa_scores'
    
    score_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    chair_score = db.Column(db.Integer, db.CheckConstraint('chair_score >= 0'), nullable=False)
    monitor_score = db.Column(db.Integer, db.CheckConstraint('monitor_score >= 0'), nullable=False)
    phone_score = db.Column(db.Integer, db.CheckConstraint('phone_score >= 0'), nullable=False)
    keyboard_score = db.Column(db.Integer, db.CheckConstraint('keyboard_score >= 0'), nullable=False)
    total_score = db.Column(db.Numeric(5, 2), db.CheckConstraint('total_score >= 0'), nullable=False)
    evaluation_date = db.Column(db.DateTime, default=func.now())
    level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)
    
    def __init__(self, user_id, chair_score, monitor_score, phone_score, keyboard_score, total_score):
        self.user_id = user_id
        self.chair_score = chair_score
        self.monitor_score = monitor_score
        self.phone_score = phone_score
        self.keyboard_score = keyboard_score
        self.total_score = total_score
    
    def __repr__(self):
        return f'<RosaScore {self.score_id}>'

# Tabla de puntajes OWAS
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class OwasScore(db.Model):
    
    __tablename__ = 'owas_scores'

    score_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    back_score = db.Column(db.Integer, db.CheckConstraint('back_score >= 0'), nullable=False)  # Puntaje de la espalda
    arms_score = db.Column(db.Integer, db.CheckConstraint('arms_score >= 0'), nullable=False)  # Puntaje de los brazos
    legs_score = db.Column(db.Integer, db.CheckConstraint('legs_score >= 0'), nullable=False)  # Puntaje de las piernas
    total_score = db.Column(db.Numeric(5, 2), db.CheckConstraint('total_score >= 0'), nullable=False)
    evaluation_date = db.Column(db.DateTime, default=datetime.utcnow)
    level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)


    def __init__(self, user_id, back_score, arms_score, legs_score, total_score):
        self.user_id = user_id
        self.back_score = back_score
        self.arms_score = arms_score
        self.legs_score = legs_score
        self.total_score = total_score

    def __repr__(self):
        return f'<OwasScore {self.score_id}>'


# Tabla de puntajes NIOSH
class NioshScore(db.Model):
    __tablename__ = 'niosh_scores'
    
    score_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    load_weight = db.Column(db.Numeric(5, 2), db.CheckConstraint('load_weight > 0'), nullable=False)
    horizontal_distance = db.Column(db.Numeric(5, 2), db.CheckConstraint('horizontal_distance > 0'), nullable=False)
    vertical_distance = db.Column(db.Numeric(5, 2), db.CheckConstraint('vertical_distance > 0'), nullable=False)
    asymmetry_angle = db.Column(db.Numeric(5, 2), db.CheckConstraint('asymmetry_angle >= 0'), nullable=False)
    frequency = db.Column(db.Integer, db.CheckConstraint('frequency > 0'), nullable=False)
    rwl = db.Column(db.Numeric(5, 2), db.CheckConstraint('rwl > 0'), nullable=False)
    evaluation_date = db.Column(db.DateTime, default=func.now())
    level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)
    
    def __init__(self, user_id, load_weight, horizontal_distance, vertical_distance, asymmetry_angle, frequency, rwl):
        self.user_id = user_id
        self.load_weight = load_weight
        self.horizontal_distance = horizontal_distance
        self.vertical_distance = vertical_distance
        self.asymmetry_angle = asymmetry_angle
        self.frequency = frequency
        self.rwl = rwl
    
    def __repr__(self):
        return f'<NioshScore {self.score_id}>'

# Tabla de planes de mejora
class ImprovementPlan(db.Model):
    __tablename__ = 'improvement_plans'
    
    plan_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    reba_score_id = db.Column(db.Integer, db.ForeignKey('reba_scores.score_id'), nullable=True)
    rosa_score_id = db.Column(db.Integer, db.ForeignKey('rosa_scores.score_id'), nullable=True)
    owas_score_id = db.Column(db.Integer, db.ForeignKey('owas_scores.score_id'), nullable=True)
    niosh_score_id = db.Column(db.Integer, db.ForeignKey('niosh_scores.score_id'), nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)
    recommendation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    
    def __init__(self, user_id, recommendation):
        self.user_id = user_id
        self.recommendation = recommendation
    
    def __repr__(self):
        return f'<ImprovementPlan {self.plan_id}>'
