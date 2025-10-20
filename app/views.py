from flask import render_template
from . import app

@app.route("/")
def main():
    return render_template("base.html")


@app.route("/homepage")
def home():
    """View for the Home page of your website."""
    agent = request.user_agent

    return render_template("home.html", agent=agent)