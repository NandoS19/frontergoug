from flask import Blueprint, render_template, request
from .models import User, RiskLevel, RebaScore, RosaScore, OwasScore, NioshScore, ImprovementPlan

bp = Blueprint('home', __name__)

def get_user(id):
    user = User.query.get_or_404(id)
    return user

#def get_post(id):
#    post = Post.query.get_or_404(id)
#    return post
#
#def search_post(query):
#    posts = Post.query.filter(Post.title.ilike(f'%{query}%')).all()
#    return posts
#
@bp.route('/')
def index():
   return render_template('index.html')
#
#@bp.route('/blog/<url>')
#def blog(url):
#    post = Post.query.filter_by(url=url).first()
#    return render_template('blog.html', post=post, get_user=get_user)