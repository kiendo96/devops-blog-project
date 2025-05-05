from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5 as Bootstrap
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from config import config
import os
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
csrf = CSRFProtect()
migrate = Migrate()

login_manager.login_view = 'admin.login'
login_manager.login_message = "Vui lòng đăng nhập để truy cập trang này."
login_manager.login_message_category = "info"


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        print(f"Checked/Created upload folder: {app.config['UPLOAD_FOLDER']}")
    except OSError as e:
        app.logger.error(f"Error creating upload folder {app.config['UPLOAD_FOLDER']}: {e}")


    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow}

    from .routes.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    return app


# @login_manager.user_loader
# def load_user(user_id):
#    from .models import User
#    return User.query.get(int(user_id))