from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, DateTimeLocalField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import datetime


class SportEventForm(FlaskForm):
    """Форма для створення та редагування спортивної події"""
    name = StringField(
        "Назва події",
        validators=[
            DataRequired(message="Назва події є обов'язковим полем"),
            Length(min=3, max=200, message="Назва повинна бути від 3 до 200 символів")
        ],
        render_kw={"class": "form-control", "placeholder": "Введіть назву спортивної події"}
    )
    
    description = TextAreaField(
        "Опис події",
        validators=[
            Length(max=1000, message="Опис не повинен перевищувати 1000 символів")
        ],
        render_kw={
            "class": "form-control",
            "rows": 5,
            "placeholder": "Опишіть подію (до 1000 символів)"
        }
    )
    
    event_date = DateTimeLocalField(
        "Дата та час події",
        validators=[DataRequired(message="Дата та час події є обов'язковими")],
        format='%Y-%m-%dT%H:%M',
        render_kw={"class": "form-control"}
    )
    
    location = StringField(
        "Місце проведення",
        validators=[
            DataRequired(message="Місце проведення є обов'язковим полем"),
            Length(min=3, max=200, message="Місце проведення повинно бути від 3 до 200 символів")
        ],
        render_kw={"class": "form-control", "placeholder": "Введіть місце проведення"}
    )
    
    price = DecimalField(
        "Ціна квитка (грн)",
        validators=[
            Optional(),
            NumberRange(min=0, message="Ціна не може бути від'ємною")
        ],
        places=2,
        render_kw={"class": "form-control", "placeholder": "0.00", "step": "0.01"}
    )
    
    sport_type_id = SelectField(
        "Вид спорту",
        validators=[DataRequired(message="Оберіть вид спорту")],
        coerce=int,
        render_kw={"class": "form-select"}
    )
    
    submit = SubmitField(
        "Зберегти",
        render_kw={"class": "btn btn-primary"}
    )
    
    def __init__(self, *args, **kwargs):
        super(SportEventForm, self).__init__(*args, **kwargs)
        # Завантажуємо види спорту з БД для select
        from app.models import SportType
        self.sport_type_id.choices = [
            (st.id, st.name) for st in SportType.query.order_by(SportType.name).all()
        ]
        if not self.sport_type_id.choices:
            self.sport_type_id.choices = [(0, "Немає доступних видів спорту")]


class SearchForm(FlaskForm):
    """Форма для пошуку подій"""
    search = StringField(
        "Пошук",
        validators=[Length(max=200)],
        render_kw={
            "class": "form-control",
            "placeholder": "Пошук за назвою або місцем проведення..."
        }
    )
    
    submit = SubmitField(
        "Шукати",
        render_kw={"class": "btn btn-outline-primary"}
    )

