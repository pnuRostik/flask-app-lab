"""Модель Post"""
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Text, DateTime, Enum, Boolean
from app import db  

class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    posted: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    category: Mapped[str] = mapped_column(
        Enum('news', 'publication', 'tech', 'other', name="post_categories"),
        default='other'
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    author: Mapped[str] = mapped_column(String(20), default='Anonymous')

    def __repr__(self):
        return f"<Post(id={self.id}, title={self.title}, category={self.category})>"
