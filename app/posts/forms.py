"""Flask-WTF форми"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField, DateTimeField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Optional
from datetime import datetime
from app import db
from app.models import User
from app.posts.models import Tag
from sqlalchemy import select


class PostForm(FlaskForm):
    """Форма для створення/редагування поста"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        stmt = select(User).order_by(User.id)
        authors = db.session.scalars(stmt).all()
        self.author_id.choices = [(a.id, a.username) for a in authors]
        
        # Завантажуємо теги для вибору
        tags_stmt = select(Tag).order_by(Tag.name)
        tags = db.session.scalars(tags_stmt).all()
        self.tags.choices = [(str(t.id), t.name) for t in tags]

    title = StringField(
        'Заголовок',
        validators=[
            DataRequired(message='Заголовок обов\'язковий'),
            Length(min=3, max=150, message='Заголовок повинен бути від 3 до 150 символів')
        ],
        render_kw={"class": "form-control"}
    )
    content = TextAreaField(
        'Зміст',
        validators=[
            DataRequired(message='Зміст обов\'язковий'),
            Length(min=10, message='Зміст повинен містити мінімум 10 символів')
        ],
        render_kw={"class": "form-control", "rows": 10}
    )
    enabled = BooleanField(
        'Активний',
        default=True,
        render_kw={"class": "form-check-input"}
    )
    publish_date = StringField(
        'Дата публікації',
        validators=[Optional()],
        default=lambda: datetime.utcnow().strftime('%Y-%m-%dT%H:%M'),
        render_kw={"class": "form-control", "type": "datetime-local", "step": "1"}
    )
    category = SelectField(
        'Категорія',
        choices=[
            ('news', 'Новини'),
            ('publication', 'Публікації'),
            ('tech', 'Технології'),
            ('other', 'Інше')
        ],
        default='other',
        validators=[DataRequired(message='Оберіть категорію')],
        render_kw={"class": "form-select"}
    )
    author_id = SelectField("Автор", coerce=int, validators=[DataRequired(message='Оберіть автора')], render_kw={"class": "form-select"})
    tags = SelectMultipleField("Теги", coerce=str, validators=[Optional()], render_kw={"class": "form-select"})
    submit = SubmitField('Зберегти', render_kw={"class": "btn btn-primary"})
