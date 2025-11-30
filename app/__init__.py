import os
import logging
from flask import Flask, render_template
from dotenv import load_dotenv
from .config import config_map
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from sqlalchemy import MetaData

# Load variables from .flaskenv or .env
load_dotenv()

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

db = SQLAlchemy(model_class=Base)
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app(config_name: str = os.environ.get("FLASK_CONFIG", "dev")) -> Flask:
    app = Flask(__name__)

    # Secret key
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Load config.py
    app.config.from_object(config_map[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Налаштування Flask-Login
    login_manager.login_view = 'users_bp.login'
    login_manager.login_message = 'Будь ласка, увійдіть в систему для доступу до цієї сторінки.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Завантажує користувача за його ID з бази даних"""
        from .models import User
        return db.session.get(User, int(user_id))


    # ------------------ LOGGING ------------------
    logging.basicConfig(
        filename="contact_form.log",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )

    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    # ---------------------------------------------

    # Import blueprints
    with app.app_context(): 
        from .users import users_bp
        from .views import main_bp    
        from .models import User
        # Register blueprints
        app.register_blueprint(main_bp)
        app.register_blueprint(users_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app
