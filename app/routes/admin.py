

import os
import uuid

from flask import (Blueprint, render_template, flash, redirect, url_for,
                   request, current_app, abort, jsonify)
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename

from .. import db
from ..models import User, Post, Project, Message
from ..forms import LoginForm, PostForm, ProjectForm

admin = Blueprint('admin', __name__)

def allowed_file(filename):
    """Kiểm tra đuôi file có hợp lệ không."""
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'gif', 'webp'})

def save_uploaded_file(file_storage):
    """Lưu file được upload, trả về URL dạng /media/... hoặc None."""
    if file_storage and file_storage.filename != '' and allowed_file(file_storage.filename):
        filename = secure_filename(file_storage.filename)
        extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{extension}"
        upload_folder = current_app.config['UPLOAD_FOLDER']
        save_path = os.path.join(upload_folder, unique_filename)
        try:
            
            os.makedirs(upload_folder, exist_ok=True)
            file_storage.save(save_path)
            media_prefix = current_app.config.get('MEDIA_URL_PREFIX', '/media/images/')
            file_url = os.path.join(media_prefix, unique_filename).replace("\\", "/")
            if not file_url.startswith('/'):
                file_url = '/' + file_url
            return file_url
        except Exception as e:
            current_app.logger.error(f"Failed to save uploaded file {filename}: {e}")
            return None
    return None


@admin.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
            return redirect(url_for('admin.login'))
        login_user(user, remember=form.remember_me.data)
        flash('Đăng nhập thành công!', 'success')
        next_page = request.args.get('next')
        safe_next_page = None
        if next_page and next_page.startswith('/'):
            admin_base_url = url_for('admin.dashboard').rsplit('/', 1)[0]
            if next_page.startswith(admin_base_url):
                 safe_next_page = next_page

            elif next_page in [url_for('main.index'), url_for('main.projects'), url_for('main.about'), url_for('main.contact'), url_for('main.blog_index')]:
                 safe_next_page = next_page
        return redirect(safe_next_page or url_for('admin.dashboard'))
    return render_template('login.html', title='Đăng nhập Admin', form=form)

@admin.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('main.index'))


@admin.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    posts = pagination.items
    return render_template('admin/dashboard.html', title='Bảng điều khiển', posts=posts, pagination=pagination)


@admin.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        file = request.files.get(form.featured_image_url.name)
        saved_image_url = save_uploaded_file(file)
        post = Post(title=form.title.data,
                    content=form.content.data,
                    featured_image_url=saved_image_url,
                    author=current_user)
        post.generate_slug()
        db.session.add(post)
        try:
            db.session.commit()
            flash('Bài viết đã được tạo thành công!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi tạo bài viết: {e}', 'danger')

    return render_template('admin/post_form.html', title='Tạo bài viết mới', form=form, legend='Bài viết mới')


@admin.route('/posts/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm()
    if form.validate_on_submit():
        title_changed = (post.title != form.title.data)
        post.title = form.title.data
        post.content = form.content.data
        file = request.files.get(form.featured_image_url.name)
        if file and file.filename != '':
            saved_image_url = save_uploaded_file(file)
            if saved_image_url:
                post.featured_image_url = saved_image_url
            else:
                 flash('Upload ảnh đại diện mới không thành công (file không hợp lệ?). Ảnh cũ được giữ lại.', 'warning')
        if title_changed:
            post.generate_slug()
        try:
            db.session.commit()
            flash('Bài viết đã được cập nhật!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật bài viết: {e}', 'danger')

    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('admin/post_form.html', title='Chỉnh sửa bài viết', form=form, post=post, legend=f'Sửa: {post.title}')

@admin.route('/posts/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    # Cân nhắc xóa file ảnh liên quan trên server/PVC ở đây nếu muốn
    # if post.featured_image_url:
    #     try:
    #         filename = post.featured_image_url.split('/')[-1] # Lấy tên file
    #         file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    #         if os.path.exists(file_path):
    #             os.remove(file_path)
    #     except Exception as e:
    #         current_app.logger.error(f"Error deleting file {post.featured_image_url}: {e}")
    db.session.delete(post)
    db.session.commit()
    flash('Bài viết đã được xóa!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin.route('/projects')
@login_required
def list_projects():
    page = request.args.get('page', 1, type=int)
    pagination = Project.query.order_by(Project.timestamp.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    projects = pagination.items
    return render_template('admin/projects_dashboard.html', title='Quản lý Dự án',
                           projects=projects, pagination=pagination)

@admin.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    form = ProjectForm()
    if form.validate_on_submit():
        file = request.files.get(form.image_url.name)
        saved_image_url = save_uploaded_file(file)
        project = Project(title=form.title.data,
                          description=form.description.data,
                          image_url=saved_image_url,
                          project_url=form.project_url.data,
                          technologies=form.technologies.data)
        db.session.add(project)
        try:
            db.session.commit()
            flash('Dự án đã được tạo thành công!', 'success')
            return redirect(url_for('admin.list_projects'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi tạo dự án: {e}', 'danger')

    return render_template('admin/project_form.html', title='Tạo dự án mới', form=form, legend='Dự án mới')


@admin.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm()
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.project_url = form.project_url.data
        project.technologies = form.technologies.data
        file = request.files.get(form.image_url.name)
        if file and file.filename != '':
            saved_image_url = save_uploaded_file(file)
            if saved_image_url:
                project.image_url = saved_image_url
            else:
                 flash('Upload ảnh dự án mới không thành công (file không hợp lệ?). Ảnh cũ được giữ lại.', 'warning')
        try:
            db.session.commit()
            flash('Dự án đã được cập nhật!', 'success')
            return redirect(url_for('admin.list_projects'))
        except Exception as e:
            db.session.rollback()
            flash(f'Lỗi khi cập nhật dự án: {e}', 'danger')

    elif request.method == 'GET':
        form.title.data = project.title
        form.description.data = project.description
        form.project_url.data = project.project_url
        form.technologies.data = project.technologies
    return render_template('admin/project_form.html', title='Chỉnh sửa dự án', form=form, project=project, legend=f'Sửa: {project.title}')

@admin.route('/projects/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Dự án đã được xóa!', 'success')
    return redirect(url_for('admin.list_projects'))

@admin.route('/messages')
@login_required
def list_messages():
    page = request.args.get('page', 1, type=int)
    pagination = Message.query.order_by(Message.timestamp.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    messages = pagination.items
    return render_template('admin/messages.html', title='Tin nhắn đã nhận',
                           messages=messages, pagination=pagination)