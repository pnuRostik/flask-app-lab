import os
from flask import Flask
from dotenv import load_dotenv

# Load variables from .flaskenv file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config.from_object('config')


import logging

# Configure logging for the application
logging.basicConfig(
    filename="contact_form.log",  
    level=logging.INFO,           
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Reduce noise from other libraries
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)

# Create logger for this module
logger = logging.getLogger(__name__)


from . import views

from .users import users_bp
from .products import products_bp

app.register_blueprint(users_bp)
app.register_blueprint(products_bp)
