import os
import logging
from flask import Flask, render_template
from dotenv import load_dotenv
from .config import config_map
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# Load variables from .flaskenv or .env
load_dotenv()

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()


def create_app(config_name: str = os.environ.get("FLASK_CONFIG", "dev")) -> Flask:
    app = Flask(__name__)

    # Secret key
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Load config.py
    app.config.from_object(config_map[config_name])

    db.init_app(app)
    migrate.init_app(app, db)


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
        from .products import products_bp
        from .posts import posts_bp
        from .views import main_bp    

        # Register blueprints
        app.register_blueprint(main_bp)
        app.register_blueprint(users_bp)
        app.register_blueprint(products_bp)
        app.register_blueprint(posts_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app
