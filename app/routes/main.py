from flask import render_template, request, abort, flash, redirect, url_for, send_from_directory, current_app
from flask import Blueprint, render_template, request, abort
from ..models import Post, Project, Message
from ..forms import ContactForm
from .. import db

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    latest_posts = Post.query.order_by(Post.timestamp.desc()).limit(3).all()
    recent_projects = Project.query.order_by(Project.timestamp.desc()).limit(3).all()
    return render_template('index.html', title='Trang chủ',
                           posts=latest_posts,
                           recent_projects=recent_projects)

@main.route('/post/<slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug).first()
    if post is None:
        abort(404)
    return render_template('post_detail.html', title=post.title, post=post)

@main.route('/projects')
def projects():
    page = request.args.get('page', 1, type=int)
    pagination = Project.query.order_by(Project.timestamp.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    projects_list = pagination.items
    return render_template('projects.html', title='Dự án',
                           projects=projects_list, pagination=pagination)

@main.route('/about')
def about():
    return render_template('about.html', title='Về tôi')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(name=form.name.data,
                      email=form.email.data,
                      subject=form.subject.data,
                      body=form.body.data)
        db.session.add(msg)
        try:
            db.session.commit()
            flash('Tin nhắn của bạn đã được gửi thành công!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Đã xảy ra lỗi khi gửi tin nhắn: {e}', 'danger')

        return redirect(url_for('main.contact'))

    return render_template('contact.html', title='Liên hệ', form=form)

@main.route('/blog')
def blog_index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=5, error_out=False
    )
    posts_list = pagination.items
    return render_template('blog.html', title='Blog',
                           posts=posts_list, pagination=pagination)
    
@main.route('/media/images/<path:filename>')
def uploaded_image_file(filename):
    upload_dir = current_app.config['UPLOAD_FOLDER']
    try:
        return send_from_directory(upload_dir, filename, as_attachment=False)
    except FileNotFoundError:
        abort(404)