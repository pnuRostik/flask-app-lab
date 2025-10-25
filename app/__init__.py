import os
from flask import Flask
from dotenv import load_dotenv

# Load variables from .flaskenv file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config.from_object('config')


from . import views

from .users import users_bp
from .products import products_bp

app.register_blueprint(users_bp)
app.register_blueprint(products_bp)
