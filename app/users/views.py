from flask import request, redirect, url_for, render_template, flash, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import logging

from . import users_bp
from .forms import ContactForm, LoginForm, RegistrationForm
from app.models import User
from app import db

# Set up logger for this module
logger = logging.getLogger(__name__)

@users_bp.route("/hi/<name>")
def greetings(name):
    name = name.upper()
    age = request.args.get("age", None, int)

    return render_template("users/hi.html", name=name, age=age)


@users_bp.route("/register", methods=["GET", "POST"])
def register():
    # Перевіряємо чи користувач вже авторизований
    if current_user.is_authenticated:
        return redirect(url_for("users_bp.profile"))

    form = RegistrationForm()
    
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        # Створюємо нового користувача
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            # Авторизуємо користувача після реєстрації
            login_user(user, remember=False)
            flash("Реєстрація успішна! Ви автоматично увійшли в систему.", "success")
            logger.info(f"New user registered and logged in: {username} ({email})")
            return redirect(url_for("users_bp.profile"))
        except Exception as e:
            db.session.rollback()
            flash("Помилка при реєстрації. Спробуйте ще раз.", "error")
            logger.error(f"Registration error: {str(e)}")
    
    if request.method == "POST" and not form.validate():
        flash("Будь ласка, виправте помилки у формі", "error")

    return render_template("users/register.html", form=form, show_navbar=False)


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    # Перевіряємо чи користувач вже авторизований
    if current_user.is_authenticated:
        return redirect(url_for("users_bp.profile"))

    form = LoginForm()
    
    if form.validate_on_submit():
        username_or_email = form.username.data
        password = form.password.data
        remember = form.remember.data

        # Шукаємо користувача за username або email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            # Авторизуємо користувача за допомогою Flask-Login
            login_user(user, remember=remember)
            
            remember_msg = " (запам'ятано)" if remember else ""
            flash(f"Успішний вхід в систему{remember_msg}!", "success")
            logger.info(f"User logged in: {user.username}")
            
            return redirect(url_for("users_bp.profile"))
        else:
            flash("Невірне ім'я користувача або пароль", "error")
            logger.warning(f"Failed login attempt: {username_or_email}")
            return redirect(url_for("users_bp.login"))
    
    if request.method == "POST" and not form.validate():
        flash("Будь ласка, виправте помилки у формі", "error")
        return redirect(url_for("users_bp.login"))

    return render_template("users/login.html", form=form, show_navbar=False)


@users_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
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
    return render_template("users/profile.html", username=current_user.username, cookies=cookies_data, theme=current_theme)

@users_bp.route("/logout")
@login_required
def logout():
    username = current_user.username
    logout_user()
    logger.info(f"User logged out: {username}")
    flash("Ви успішно вийшли з системи", "success")
    return redirect(url_for("users_bp.login"))

@users_bp.route("/change-theme/<theme>")
@login_required
def change_theme(theme):
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
        flash("Будь ласка, виправте помилки у формі", "danger")
    return render_template("users/contact.html", form=form)

@users_bp.route("/list")
@login_required
def users_list():
    """Сторінка зі списком всіх користувачів (тільки для авторизованих)"""
    users = User.query.all()
    return render_template("users/users_list.html", users=users)

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