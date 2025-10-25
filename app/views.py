from flask import render_template, redirect, url_for, request
from . import app



@app.route('/')
def index():
    return redirect(url_for('users_bp.login'))


@app.route("/homepage")
def home():
    """View for the Home page of your website."""
    agent = request.user_agent

    return render_template("home.html", agent=agent)