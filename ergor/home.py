from flask import Blueprint, render_template, request
from .models import User, RiskLevel, RebaScore, RosaScore, OwasScore, NioshScore

bp = Blueprint('home', __name__)

def get_user(id):
    user = User.query.get_or_404(id)
    return user

@bp.route('/')
def index():
   return render_template('index.html')
