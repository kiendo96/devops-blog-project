from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from slugify import slugify
from . import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    project_url = db.Column(db.String(255), nullable=True)
    technologies = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Project {self.title}>'

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, index=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    featured_image_url = db.Column(db.String(255), nullable=True)

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)
        pass

    def generate_slug(self):
        if not self.title:
            self.slug = f"post-{self.id}" if self.id else f"untitled-{int(datetime.utcnow().timestamp())}"
            return

        base_slug = slugify(self.title)
        if not base_slug:
             base_slug = f"post-{self.id}" if self.id else f"untitled-{int(datetime.utcnow().timestamp())}"

        unique_slug = base_slug
        count = 1
        while True:
            query = Post.query.filter(Post.slug == unique_slug)
            if self.id:
                query = query.filter(Post.id != self.id)
            conflicting_post = query.first()
            if not conflicting_post:
                break
            else:
                count += 1
                unique_slug = f"{base_slug}-{count}"

        self.slug = unique_slug

    def __repr__(self):
        return f'<Post {self.title}>'

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(150), nullable=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message from {self.name}>'