from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Text, ForeignKey, Numeric
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


class SportType(db.Model):
    """Додаткова модель - вид спорту"""
    __tablename__ = "sport_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=True)  # наприклад: командний, індивідуальний

    # Зв'язок з основними подіями
    events: Mapped[list["SportEvent"]] = relationship("SportEvent", back_populates="sport_type", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SportType(id={self.id}, name={self.name})>"


class SportEvent(db.Model):
    """Основна модель - спортивна подія"""
    __tablename__ = "sport_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    event_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Зовнішній ключ до виду спорту
    sport_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("sport_types.id"), nullable=False)
    
    # Зовнішній ключ до користувача (хто створив)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Зв'язки
    sport_type: Mapped["SportType"] = relationship("SportType", back_populates="events")
    user: Mapped["User"] = relationship("User")

    def __repr__(self):
        return f"<SportEvent(id={self.id}, name={self.name}, date={self.event_date})>"

 
