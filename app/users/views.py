from flask import request, redirect, url_for, render_template, flash, session, make_response
from datetime import datetime, timedelta
import logging

from . import users_bp
from .forms import ContactForm, LoginForm

# Set up logger for this module
logger = logging.getLogger(__name__)

VALID_USERNAME = "user1"
VALID_PASSWORD = "pass123"

@users_bp.route("/hi/<name>")
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, int)

    return render_template("users/hi.html", name=name, age=age)


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    # Перевіряємо чи користувач вже авторизований
    if "username" in session:
        return redirect(url_for("users_bp.profile"))

    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session["username"] = username
            
            remember_msg = " (запам'ятано)" if remember else ""
            flash(f"Успішний вхід в систему{remember_msg}!", "success")
            
            return redirect(url_for("users_bp.profile"))
        else:
            flash("Невірне ім'я користувача або пароль", "error")
            return redirect(url_for("users_bp.login"))
    
    if request.method == "POST" and not form.validate():
        flash("Будь ласка, виправте помилки у формі", "error")
        return redirect(url_for("users_bp.login"))

    return render_template("users/login.html", form=form, show_navbar=False)


@users_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if "username" not in session:
        flash("Ви не авторизовані", "error")
        return redirect(url_for("users_bp.login"))
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add_cookie":
            key = request.form.get("cookie_key")
            value = request.form.get("cookie_value")
            expiry_days = int(request.form.get("expiry_days", 30))
            
            if key and value:
                response = make_response(redirect(url_for("users_bp.profile")))
                expiry_date = datetime.now() + timedelta(days=expiry_days)
                response.set_cookie(key, value, expires=expiry_date)
                flash(f"Cookie '{key}' успішно додано", "success")
                return response
            else:
                flash("Ключ та значення cookie не можуть бути порожніми", "error")
        
        elif action == "delete_cookie":
            key = request.form.get("cookie_key")
            if key:
                response = make_response(redirect(url_for("users_bp.profile")))
                response.set_cookie(key, "", expires=0)
                flash(f"Cookie '{key}' успішно видалено", "success")
                return response
        
        elif action == "delete_all_cookies":
            response = make_response(redirect(url_for("users_bp.profile")))
            for key in request.cookies.keys():
                if key != 'session':  
                    response.set_cookie(key, "", expires=0)
            flash("Всі cookies успішно видалено", "success")
            return response
    
   
    cookies_data = []
    for key, value in request.cookies.items():
        if key != 'session': 
            cookies_data.append({"key": key, "value": value})
    
    current_theme = session.get("theme", "light")
    return render_template("users/profile.html", username=session["username"], cookies=cookies_data, theme=current_theme)

@users_bp.route("/logout")
def logout():
    session.pop("username", None)
    flash("Ви успішно вийшли з системи", "success")
    return redirect(url_for("users_bp.login"))

@users_bp.route("/change-theme/<theme>")
def change_theme(theme):
    if "username" not in session:
        flash("Ви не авторизовані", "error")
        return redirect(url_for("users_bp.login"))
    
    if theme in ["light", "dark"]:
        session["theme"] = theme
        flash(f"Тема змінена на {theme}", "success")
    else:
        flash("Невірна тема", "error")
    
    return redirect(url_for("users_bp.profile"))


@users_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        subject = form.subject.data
        message = form.message.data
        
        # Log the contact form submission
        logger.info(
            f"Contact form submitted - Name: {name}, Email: {email}, "
            f"Phone: {phone}, Subject: {subject}, Message length: {len(message)} chars"
        )
        
        flash(f"Дякуємо за ваше повідомлення, {name} {email}! Ми зв'яжемося з вами найближчим часом.", "success")
        return redirect(url_for("users_bp.profile"))
    
    # Log form validation errors if POST request
    if request.method == "POST" and not form.validate():
        flash("Будь ласка, виправте помилки у формі", "error")
    return render_template("users/contact.html", form=form)

@users_bp.route("/admin")
def admin():
    to_url = url_for(
        "users_bp.greetings",
        name="administrator",
        age=45,
        _external=True
    )
    print(to_url)
    return redirect(to_url)