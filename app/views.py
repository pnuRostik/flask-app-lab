from flask import render_template, redirect, url_for, request, Blueprint

# Create a blueprint for main views
main_bp = Blueprint('main', __name__)



@main_bp.route('/')
def index():
    return redirect(url_for('users_bp.login'))


@main_bp.route("/homepage")
def home():
    """View for the Home page of your website."""
    agent = request.user_agent

    return render_template("home.html", agent=agent)