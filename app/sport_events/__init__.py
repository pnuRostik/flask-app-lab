from flask import Blueprint

sport_events_bp = Blueprint(
    "sport_events_bp",
    __name__,
    url_prefix="/sport-events",
    template_folder="templates"
)

from . import views

