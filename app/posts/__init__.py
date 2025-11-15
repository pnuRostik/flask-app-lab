"""Ініціалізація блюпринта"""
import os
from flask import Blueprint

# Отримуємо абсолютний шлях до папки static


posts_bp = Blueprint(
    "posts_bp",
    __name__,
    url_prefix="",
    template_folder="templates",
    static_folder='static',
    static_url_path="/posts/static"
)

from . import views

