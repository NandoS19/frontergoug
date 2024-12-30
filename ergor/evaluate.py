from flask import Blueprint, render_template, request, redirect, url_for, flash,g
from .auth import login_required
from ergor import db

bp = Blueprint('evaluate', __name__, url_prefix='/evaluate') 

@bp.route('/evaluate')
@login_required
def evaluate_page():
    return f'Pagina de evaluacion'

@bp.route('/results')
@login_required
def results_page():
    return f'Pagina de resultados'

# @bp.route('/posts')
# @login_required
# def posts():
#     posts = Post.query.all()
#     return render_template('admin/posts.html', posts=posts)  

# @bp.route('/create', methods=('GET', 'POST'))
# @login_required
# def create():
#     if request.method == 'POST':
#         url = request.form.get('url')
#         url = url.replace(' ', '-')
#         title = request.form.get('title')
#         info = request.form.get('info')
#         content = request.form.get('ckeditor')
#         error = None
        
#         post = Post(g.user.id, url, title, info, content)
#         post_url = Post.query.filter_by(url=url).first()
#         if post_url == None:
#             db.session.add(post)
#             db.session.commit()
#             flash(f'Publicación {post.title} creada exitosamente', 'success')
#             return redirect(url_for('post.posts'))
#         else:
#             error = f'La URL {url} ya existe'
#         flash(error)
#     return render_template('admin/create.html')

# @bp.route('/update/<int:id>', methods=('GET', 'POST'))
# def update(id):
#     post = Post.query.get_or_404(id)
    
#     if request.method == 'POST':
#         post.title = request.form.get('title')
#         post.info = request.form.get('info')
#         post.content = request.form.get('ckeditor')
        
#         db.session.commit()
#         flash(f'Publicación {post.title} actualizada exitosamente', 'success')
#         return redirect(url_for('post.posts'))
    
#     return render_template('admin/update.html', post=post)

# @bp.route('/delete/<int:id>')
# @login_required
# def delete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash(f'Publicación {post.title} eliminada exitosamente', 'success')
    return redirect(url_for('post.posts'))