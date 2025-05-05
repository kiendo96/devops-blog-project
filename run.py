from app import create_app, db
from app.models import User, Post
import os


app = create_app(os.getenv('FLASK_ENV') or 'default')

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}

@app.cli.command('init-db')
def init_db_command():
    print("Đang tạo các bảng database...")

    with app.app_context():
         try:
             db.create_all()
             print("Tạo bảng thành công!")
         except Exception as e:
             print(f"Lỗi khi tạo bảng: {e}")
         
@app.cli.command('create-admin')
def create_admin_command():
    with app.app_context():
        username = input("Nhập tên đăng nhập admin: ")
        password = input("Nhập mật khẩu admin: ")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"Lỗi: Tên đăng nhập '{username}' đã tồn tại.")
            return  
        new_admin_user = User(username=username)
        new_admin_user.set_password(password)

        try:
            db.session.add(new_admin_user)
            db.session.commit()
            print(f"Tạo admin user '{username}' thành công!")
        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi tạo admin user: {e}")

if __name__ == '__main__':
    app.run()