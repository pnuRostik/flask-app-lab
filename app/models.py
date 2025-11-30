from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Text
from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    image: Mapped[str] = mapped_column(String(120), nullable=True, default='profile_default.jpg')
    about_me: Mapped[str] = mapped_column(Text, nullable=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        """Встановлює хеш пароля користувача"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Перевіряє чи пароль відповідає хешу"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

 
