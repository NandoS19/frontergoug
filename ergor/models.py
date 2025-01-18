# Description: Archivo que contiene las clases de los modelos de la base de datos.
from ergor import db
from datetime import datetime
from sqlalchemy.sql import func

# Tabla de usuarios
class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    photo = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=func.now())  # Campo opcional recomendado
    last_login = db.Column(db.DateTime, nullable=True)  # Campo opcional recomendado

    # Relaciones
    employees = db.relationship('Employe', backref='user', cascade='all, delete-orphan')  # Relación con empleados

    def __init__(self, username, email, password, photo=None):
        self.username = username
        self.email = email
        self.password = password
        self.photo = photo

    def __repr__(self):
        return f'<User {self.username}>'

# Tabla de empleados
class Employe(db.Model):
    __tablename__ = 'employe'
    
    employe_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    work = db.Column(db.String(50), nullable=False)
    time_company = db.Column(db.String(10), nullable=False)
    job_title = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, db.CheckConstraint('age >= 0'), nullable=True)
    height = db.Column(db.Numeric(5, 2), db.CheckConstraint('height > 0'), nullable=True)
    weight = db.Column(db.Numeric(5, 2), db.CheckConstraint('weight > 0'), nullable=True)
    gender = db.Column(db.String(20), db.CheckConstraint("gender IN ('Masculino', 'Femenino', 'Otro')"), nullable=True)
    hours = db.Column(db.Integer, db.CheckConstraint('hours >= 0'), nullable=True)
    video_path = db.Column(db.String(100))

    # Clave foránea que establece la relación con User
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    # Relaciones con puntajes
    reba_scores = db.relationship('RebaScore', backref='employe', cascade='all, delete-orphan')
    rosa_scores = db.relationship('RosaScore', backref='employe', cascade='all, delete-orphan')
    owas_scores = db.relationship('OwasScore', backref='employe', cascade='all, delete-orphan')
    niosh_scores = db.relationship('NioshScore', backref='employe', cascade='all, delete-orphan')
    generate_plans = db.relationship('GeneratePlan', backref='employe', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Employe {self.name} {self.last_name}>'

# Tabla de niveles de riesgo
class RiskLevel(db.Model):
    __tablename__ = 'risk_levels'
    
    level_id = db.Column(db.Integer, primary_key=True)
    risk_level = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<RiskLevel {self.risk_level}>'

# Tabla de puntajes REBA
class RebaScore(db.Model):
    __tablename__ = 'reba_scores'
    
    score_id = db.Column(db.Integer, primary_key=True)
    employe_id = db.Column(db.Integer, db.ForeignKey('employe.employe_id'), nullable=False)
    trunk_score = db.Column(db.Integer, db.CheckConstraint('trunk_score >= 0'), nullable=False)
    neck_score = db.Column(db.Integer, db.CheckConstraint('neck_score >= 0'), nullable=False)
    leg_score = db.Column(db.Integer, db.CheckConstraint('leg_score >= 0'), nullable=False)
    arm_score = db.Column(db.Integer, db.CheckConstraint('arm_score >= 0'), nullable=False)
    forearm_score = db.Column(db.Integer, db.CheckConstraint('forearm_score >= 0'), nullable=False)
    wrist_score = db.Column(db.Integer, db.CheckConstraint('wrist_score >= 0'), nullable=False)
    group_a_score = db.Column(db.Integer, db.CheckConstraint('group_a_score >= 0'), nullable=True)
    group_b_score = db.Column(db.Integer, db.CheckConstraint('group_b_score >= 0'), nullable=True)
    total_score = db.Column(db.Integer, db.CheckConstraint('total_score >= 0'), nullable=True)

    def __repr__(self):
        return f'<RebaScore {self.score_id}>'

# Tabla de puntajes ROSA
class RosaScore(db.Model):
    __tablename__ = 'rosa_scores'
    
    score_id = db.Column(db.Integer, primary_key=True)
    employe_id = db.Column(db.Integer, db.ForeignKey('employe.employe_id'), nullable=False)
    chair_score = db.Column(db.Integer, db.CheckConstraint('chair_score >= 0'), nullable=False)
    monitor_score = db.Column(db.Integer, db.CheckConstraint('monitor_score >= 0'), nullable=False)
    phone_score = db.Column(db.Integer, db.CheckConstraint('phone_score >= 0'), nullable=False)
    keyboard_score = db.Column(db.Integer, db.CheckConstraint('keyboard_score >= 0'), nullable=False)
    total_score = db.Column(db.Numeric(5, 2), db.CheckConstraint('total_score >= 0'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)

    def __repr__(self):
        return f'<RosaScore {self.score_id}>'

# Tabla de planes de mejora
class GeneratePlan(db.Model):
    __tablename__ = 'generate_plan'
    
    plan_id = db.Column(db.Integer, primary_key=True)
    employe_id = db.Column(db.Integer, db.ForeignKey('employe.employe_id'), nullable=False)
    reba_score_id = db.Column(db.Integer, db.ForeignKey('reba_scores.score_id'), nullable=True)
    rosa_score_id = db.Column(db.Integer, db.ForeignKey('rosa_scores.score_id'), nullable=True)
    owas_score_id = db.Column(db.Integer, db.ForeignKey('owas_scores.score_id'), nullable=True)
    niosh_score_id = db.Column(db.Integer, db.ForeignKey('niosh_scores.score_id'), nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)
    recommendation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())

    def __repr__(self):
        return f'<GeneratePlan {self.plan_id}>'
    __tablename__ = 'generate_plan'
    
    plan_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    employe_id = db.Column(db.Integer, db.ForeignKey('employe.employe_id'), nullable=False)
    reba_score_id = db.Column(db.Integer, db.ForeignKey('reba_scores.score_id'), nullable=True)
    rosa_score_id = db.Column(db.Integer, db.ForeignKey('rosa_scores.score_id'), nullable=True)
    owas_score_id = db.Column(db.Integer, db.ForeignKey('owas_scores.score_id'), nullable=True)
    niosh_score_id = db.Column(db.Integer, db.ForeignKey('niosh_scores.score_id'), nullable=True)
    level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)
    recommendation = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())  # Campo opcional recomendado
    
    def __init__(self, user_id, recommendation):
        self.user_id = user_id
        self.recommendation = recommendation
        
    def __repr__(self):
        return f'<GeneratePlan {self.plan_id}>'

# # Tabla de usuarios
# class User(db.Model):
#     __tablename__ = 'users'
    
#     user_id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), nullable=False, unique=True)
#     email = db.Column(db.String(50), nullable=False)
#     password = db.Column(db.Text, nullable=False)
#     photo = db.Column(db.String(50))
#     video_path = db.Column(db.String(100))
#     age = db.Column(db.Integer,  nullable=True)
#     height = db.Column(db.Numeric(5, 2),  nullable=True)
#     weight = db.Column(db.Numeric(5, 2),  nullable=True)
#     hours = db.Column(db.Numeric(2),  nullable=True)
#     gender = db.Column(db.String(20), nullable=True)
#     job_title = db.Column(db.String(100), nullable=True)
#     created_at = db.Column(db.DateTime, default=func.now())
#     last_login = db.Column(db.DateTime, nullable=True)

#     reba_scores = db.relationship('RebaScore', backref='user', cascade='all, delete-orphan')
#     rosa_scores = db.relationship('RosaScore', backref='user', cascade='all, delete-orphan')
#     owas_scores = db.relationship('OwasScore', backref='user', cascade='all, delete-orphan')
#     niosh_scores = db.relationship('NioshScore', backref='user', cascade='all, delete-orphan')
#     improvement_plans = db.relationship('ImprovementPlan', backref='user', cascade='all, delete-orphan')
    
    
#     def __init__(self, username, email, password, photo = None, video_path = None, age=None, height=None, weight=None, hours = None, gender=None, job_title=None):
#         self.username = username
#         self.email = email
#         self.password = password
#         self.photo = photo
#         self.video_path = video_path
#         self.age = age
#         self.height = height
#         self.weight = weight
#         self.hours = hours
#         self.gender = gender
#         self.job_title = job_title
        
#     def __repr__(self):
#         return f'<User {self.username}>'
        

# # Tabla de niveles de riesgo
# class RiskLevel(db.Model):
#     __tablename__ = 'risk_levels'
    
#     level_id = db.Column(db.Integer, primary_key=True)
#     risk_level = db.Column(db.String(50), nullable=False, unique=True)
#     description = db.Column(db.Text, nullable=True)

#     reba_scores = db.relationship('RebaScore', backref='risk_level', cascade='all, delete')
#     rosa_scores = db.relationship('RosaScore', backref='risk_level', cascade='all, delete')
#     owas_scores = db.relationship('OwasScore', backref='risk_level', cascade='all, delete')
#     niosh_scores = db.relationship('NioshScore', backref='risk_level', cascade='all, delete')
#     improvement_plans = db.relationship('ImprovementPlan', backref='risk_level', cascade='all, delete')
    
#     def __init__(self, risk_level, description=None):
#         self.risk_level = risk_level
#         self.description = description
    
#     def __repr__(self):
#         return f'<RiskLevel {self.risk_level}>'

# # Tabla de puntajes REBA
# class RebaScore(db.Model):
#     __tablename__ = 'reba_scores'
    
#     score_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
#     trunk_score = db.Column(db.Integer, db.CheckConstraint('trunk_score >= 0'), nullable=False)
#     neck_score = db.Column(db.Integer, db.CheckConstraint('neck_score >= 0'), nullable=False)
#     leg_score = db.Column(db.Integer, db.CheckConstraint('leg_score >= 0'), nullable=False)
#     arm_score = db.Column(db.Integer, db.CheckConstraint('arm_score >= 0'), nullable=False)
#     forearm_score = db.Column(db.Integer, db.CheckConstraint('forearm_score >= 0'), nullable=False)
#     wrist_score = db.Column(db.Integer, db.CheckConstraint('wrist_score >= 0'), nullable=False)
#     group_a_score = db.Column(db.Integer, db.CheckConstraint('group_a_score >= 0'), nullable=False)
#     group_b_score = db.Column(db.Integer, db.CheckConstraint('group_b_score >= 0'), nullable=False)
#     total_score = db.Column(db.Integer, db.CheckConstraint('total_score >= 0'), nullable=False)
#     evaluation_date = db.Column(db.DateTime, default=func.now())
#     level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)
    
#     def __init__(self, user_id, trunk_score, neck_score, leg_score, arm_score, forearm_score, wrist_score, group_a_score, group_b_score, total_score):
#         self.user_id = user_id
#         self.trunk_score = trunk_score
#         self.neck_score = neck_score
#         self.leg_score = leg_score
#         self.arm_score = arm_score
#         self.forearm_score = forearm_score
#         self.wrist_score = wrist_score
#         self.group_a_score = group_a_score
#         self.group_b_score = group_b_score
#         self.total_score = total_score
    
#     def __repr__(self):
#         return f'<RebaScore {self.score_id}>'


# # Tabla de puntajes ROSA
# class RosaScore(db.Model):
#     __tablename__ = 'rosa_scores'
    
#     score_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
#     chair_score = db.Column(db.Integer, db.CheckConstraint('chair_score >= 0'), nullable=False)
#     monitor_score = db.Column(db.Integer, db.CheckConstraint('monitor_score >= 0'), nullable=False)
#     phone_score = db.Column(db.Integer, db.CheckConstraint('phone_score >= 0'), nullable=False)
#     keyboard_score = db.Column(db.Integer, db.CheckConstraint('keyboard_score >= 0'), nullable=False)
#     total_score = db.Column(db.Numeric(5, 2), db.CheckConstraint('total_score >= 0'), nullable=False)
#     evaluation_date = db.Column(db.DateTime, default=func.now())
#     level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)
    
#     def __init__(self, user_id, chair_score, monitor_score, phone_score, keyboard_score, total_score):
#         self.user_id = user_id
#         self.chair_score = chair_score
#         self.monitor_score = monitor_score
#         self.phone_score = phone_score
#         self.keyboard_score = keyboard_score
#         self.total_score = total_score
    
#     def __repr__(self):
#         return f'<RosaScore {self.score_id}>'

# # Tabla de puntajes OWAS
# class OwasScore(db.Model):
    
#     __tablename__ = 'owas_scores'

#     score_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
#     back_score = db.Column(db.Integer, db.CheckConstraint('back_score >= 0'), nullable=False)  # Puntaje de la espalda
#     arms_score = db.Column(db.Integer, db.CheckConstraint('arms_score >= 0'), nullable=False)  # Puntaje de los brazos
#     legs_score = db.Column(db.Integer, db.CheckConstraint('legs_score >= 0'), nullable=False)  # Puntaje de las piernas
#     total_score = db.Column(db.Numeric(5, 2), db.CheckConstraint('total_score >= 0'), nullable=False)
#     evaluation_date = db.Column(db.DateTime, default=datetime.utcnow)
#     level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)


#     def __init__(self, user_id, back_score, arms_score, legs_score, total_score):
#         self.user_id = user_id
#         self.back_score = back_score
#         self.arms_score = arms_score
#         self.legs_score = legs_score
#         self.total_score = total_score

#     def __repr__(self):
#         return f'<OwasScore {self.score_id}>'


# # Tabla de puntajes NIOSH
# class NioshScore(db.Model):
#     __tablename__ = 'niosh_scores'
    
#     score_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
#     load_weight = db.Column(db.Numeric(5, 2), db.CheckConstraint('load_weight > 0'), nullable=False)
#     horizontal_distance = db.Column(db.Numeric(5, 2), db.CheckConstraint('horizontal_distance > 0'), nullable=False)
#     vertical_distance = db.Column(db.Numeric(5, 2), db.CheckConstraint('vertical_distance > 0'), nullable=False)
#     asymmetry_angle = db.Column(db.Numeric(5, 2), db.CheckConstraint('asymmetry_angle >= 0'), nullable=False)
#     frequency = db.Column(db.Integer, db.CheckConstraint('frequency > 0'), nullable=False)
#     displacement_distance = db.Column(db.Numeric(5, 2), db.CheckConstraint('displacement_distance > 0'), nullable=False)
#     grip_quality = db.Column(db.String(10), nullable=False)  # "bueno", "regular", "malo"
#     rwl = db.Column(db.Numeric(5, 2), db.CheckConstraint('rwl > 0'), nullable=False)
#     evaluation_date = db.Column(db.DateTime, default=func.now())
#     level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)
    
#     def __init__(self, user_id, load_weight, horizontal_distance, vertical_distance, asymmetry_angle, frequency, displacement_distance, grip_quality, rwl):
#         self.user_id = user_id
#         self.load_weight = load_weight
#         self.horizontal_distance = horizontal_distance
#         self.vertical_distance = vertical_distance
#         self.asymmetry_angle = asymmetry_angle
#         self.frequency = frequency
#         self.displacement_distance = displacement_distance
#         self.grip_quality = grip_quality
#         self.rwl = rwl
    
#     def __repr__(self):
#         return f'<NioshScore {self.score_id}>'

# # Tabla de planes de mejora
# class ImprovementPlan(db.Model):
#     __tablename__ = 'improvement_plans'
    
#     plan_id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
#     reba_score_id = db.Column(db.Integer, db.ForeignKey('reba_scores.score_id'), nullable=True)
#     rosa_score_id = db.Column(db.Integer, db.ForeignKey('rosa_scores.score_id'), nullable=True)
#     owas_score_id = db.Column(db.Integer, db.ForeignKey('owas_scores.score_id'), nullable=True)
#     niosh_score_id = db.Column(db.Integer, db.ForeignKey('niosh_scores.score_id'), nullable=True)
#     level_id = db.Column(db.Integer, db.ForeignKey('risk_levels.level_id'), nullable=True)
#     recommendation = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=func.now())
    
#     def __init__(self, user_id, recommendation):
#         self.user_id = user_id
#         self.recommendation = recommendation
    
#     def __repr__(self):
#         return f'<ImprovementPlan {self.plan_id}>'
