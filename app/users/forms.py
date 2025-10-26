from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DecimalField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Email, Regexp



class ContactForm(FlaskForm):
    name = StringField(
        "Ім'я", 
        validators=[
            DataRequired(message="Ім'я є обов'язковим полем"),
            Length(min=4, max=10, message="Ім'я повинно бути від 4 до 10 символів")
        ],
        render_kw={"class": "form-control", "placeholder": "Введіть ваше ім'я"}
    )
    
    email = StringField(
        "Email", 
        validators=[
            DataRequired(message="Email є обов'язковим полем"),
            Email(message="Введіть коректний email адрес")
        ],
        render_kw={"class": "form-control", "placeholder": "example@email.com"}
    )
    
    phone = StringField(
        "Телефон", 
        validators=[
            Regexp(
                r'^\+380\d{9}$', 
                message="Телефон повинен бути у форматі +380XXXXXXXXX"
            )
        ],
        render_kw={"class": "form-control", "placeholder": "+380XXXXXXXXX"}
    )
    
    subject = SelectField(
        "Тема звернення",
        choices=[
            ('', 'Оберіть тему звернення'),
            ('general', 'Загальні питання'),
            ('support', 'Технічна підтримка'),
            ('billing', 'Питання по оплаті'),
            ('partnership', 'Співпраця'),
            ('feedback', 'Відгуки та пропозиції'),
            ('other', 'Інше')
        ],
        validators=[DataRequired(message="Оберіть тему звернення")],
        render_kw={"class": "form-select"}
    )
    
    message = TextAreaField(
        "Повідомлення",
        validators=[
            DataRequired(message="Повідомлення є обов'язковим полем"),
            Length(max=500, message="Повідомлення не повинно перевищувати 500 символів")
        ],
        render_kw={
            "class": "form-control", 
            "rows": 5, 
            "placeholder": "Введіть ваше повідомлення (до 500 символів)"
        }
    )
    
    submit = SubmitField(
        "Надіслати повідомлення",
        render_kw={"class": "btn btn-primary"}
    )

class LoginForm(FlaskForm):
    username = StringField(
        "Ім'я користувача або Email",
        validators=[
            DataRequired(message="Поле є обов'язковим")
        ],
        render_kw={"class": "form-control", "placeholder": "Введіть ім'я користувача або email"}
    )
    
    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Пароль є обов'язковим"),
            Length(min=4, max=10, message="Пароль повинен бути від 4 до 10 символів")
        ],
        render_kw={"class": "form-control", "placeholder": "Введіть пароль"}
    )
    
    remember = BooleanField(
        "Запам'ятати мене",
        render_kw={"class": "form-check-input"}
    )
    
    submit = SubmitField(
        "Увійти",
        render_kw={"class": "btn btn-primary"}
    )