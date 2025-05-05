from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional, URL, Email
from flask_wtf.file import FileField, FileAllowed
from .models import User

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


class LoginForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Mật khẩu', validators=[DataRequired()])
    remember_me = BooleanField('Ghi nhớ đăng nhập')
    submit = SubmitField('Đăng nhập')

class PostForm(FlaskForm):
    title = StringField('Tiêu đề', validators=[DataRequired(), Length(max=150)])
    content = TextAreaField('Nội dung', validators=[DataRequired()])
    featured_image_url = FileField('Ảnh đại diện bài viết (Upload)', validators=[
        FileAllowed(ALLOWED_IMAGE_EXTENSIONS, 'Chỉ chấp nhận file ảnh!')
    ])
    submit = SubmitField('Lưu bài viết')

class ProjectForm(FlaskForm):
    title = StringField('Tên dự án', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Mô tả dự án')
    image_url = FileField('Hình ảnh dự án (Upload)', validators=[
        FileAllowed(ALLOWED_IMAGE_EXTENSIONS, 'Chỉ chấp nhận file ảnh!')
    ])
    project_url = StringField('URL Dự án (Live/Repo)', validators=[Optional(), Length(max=255)])
    technologies = StringField('Công nghệ sử dụng (cách nhau bởi dấu phẩy)', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Lưu Dự án')
    
class ContactForm(FlaskForm):
    name = StringField('Tên của bạn', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    subject = StringField('Tiêu đề', validators=[Optional(), Length(max=150)])
    body = TextAreaField('Nội dung tin nhắn', validators=[DataRequired()])
    submit = SubmitField('Gửi tin nhắn')
# Optional: Form đăng ký admin
# class RegistrationForm(FlaskForm):
#     username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
#     password = PasswordField('Password', validators=[DataRequired()])
#     password2 = PasswordField(
#         'Repeat Password', validators=[DataRequired(), EqualTo('password')])
#     submit = SubmitField('Register')

#     def validate_username(self, username):
#         user = User.query.filter_by(username=username.data).first()
#         if user is not None:
#             raise ValidationError('Please use a different username.')