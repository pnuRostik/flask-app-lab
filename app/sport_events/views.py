from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
import logging

from . import sport_events_bp
from .forms import SportEventForm, SearchForm
from app.models import SportEvent, SportType
from app import db

logger = logging.getLogger(__name__)


@sport_events_bp.route("/")
def events_list():
    """Список усіх спортивних подій з можливістю сортування та пошуку"""
    # Параметри сортування
    sort_by = request.args.get("sort_by", "event_date")
    sort_order = request.args.get("sort_order", "asc")
    
    # Валідація параметрів сортування
    valid_sort_fields = ["name", "event_date", "location", "price", "created_at"]
    if sort_by not in valid_sort_fields:
        sort_by = "event_date"
    
    if sort_order not in ["asc", "desc"]:
        sort_order = "asc"
    
    # Запит до БД
    query = SportEvent.query
    
    # Пошук
    search_form = SearchForm()
    search_query = request.args.get("search", "")
    if search_query:
        search_form.search.data = search_query
        query = query.filter(
            or_(
                SportEvent.name.ilike(f"%{search_query}%"),
                SportEvent.location.ilike(f"%{search_query}%")
            )
        )
    
    # Сортування
    sort_column = getattr(SportEvent, sort_by)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)
    
    # Пагінація
    page = request.args.get("page", 1, type=int)
    per_page = 10
    events = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        "sport_events/list.html",
        events=events,
        search_form=search_form,
        sort_by=sort_by,
        sort_order=sort_order
    )


@sport_events_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_event():
    """Створення нової спортивної події"""
    form = SportEventForm()
    
    if form.validate_on_submit():
        event = SportEvent(
            name=form.name.data,
            description=form.description.data,
            event_date=form.event_date.data,
            location=form.location.data,
            price=float(form.price.data) if form.price.data else None,
            sport_type_id=form.sport_type_id.data,
            user_id=current_user.id
        )
        
        try:
            db.session.add(event)
            db.session.commit()
            flash("Спортивна подія успішно створена!", "success")
            logger.info(f"Sport event created: {event.name} by user {current_user.username}")
            return redirect(url_for("sport_events_bp.event_detail", event_id=event.id))
        except Exception as e:
            db.session.rollback()
            flash("Помилка при створенні події. Спробуйте ще раз.", "error")
            logger.error(f"Error creating sport event: {str(e)}")
    
    if request.method == "POST" and not form.validate():
        flash("Будь ласка, виправте помилки у формі", "error")
    
    return render_template("sport_events/create.html", form=form)


@sport_events_bp.route("/<int:event_id>")
def event_detail(event_id):
    """Детальна інформація про спортивну подію"""
    event = SportEvent.query.get_or_404(event_id)
    
    # Перевірка чи користувач є власником
    is_owner = current_user.is_authenticated and event.user_id == current_user.id
    
    return render_template(
        "sport_events/detail.html",
        event=event,
        is_owner=is_owner
    )


@sport_events_bp.route("/<int:event_id>/edit", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    """Редагування спортивної події (тільки для власника)"""
    event = SportEvent.query.get_or_404(event_id)
    
    # Перевірка чи користувач є власником
    if event.user_id != current_user.id:
        abort(403)
    
    form = SportEventForm(obj=event)
    
    if form.validate_on_submit():
        event.name = form.name.data
        event.description = form.description.data
        event.event_date = form.event_date.data
        event.location = form.location.data
        event.price = float(form.price.data) if form.price.data else None
        event.sport_type_id = form.sport_type_id.data
        
        try:
            db.session.commit()
            flash("Спортивна подія успішно оновлена!", "success")
            logger.info(f"Sport event updated: {event.name} by user {current_user.username}")
            return redirect(url_for("sport_events_bp.event_detail", event_id=event.id))
        except Exception as e:
            db.session.rollback()
            flash("Помилка при оновленні події. Спробуйте ще раз.", "error")
            logger.error(f"Error updating sport event: {str(e)}")
    
    if request.method == "POST" and not form.validate():
        flash("Будь ласка, виправте помилки у формі", "error")
    
    # Заповнюємо форму поточними значеннями
    if request.method == "GET":
        form.name.data = event.name
        form.description.data = event.description
        # DateTimeLocalField очікує об'єкт datetime, не рядок
        form.event_date.data = event.event_date
        form.location.data = event.location
        form.price.data = event.price
        form.sport_type_id.data = event.sport_type_id
    
    return render_template("sport_events/edit.html", form=form, event=event)


@sport_events_bp.route("/<int:event_id>/delete", methods=["POST"])
@login_required
def delete_event(event_id):
    """Видалення спортивної події (тільки для власника)"""
    event = SportEvent.query.get_or_404(event_id)
    
    # Перевірка чи користувач є власником
    if event.user_id != current_user.id:
        abort(403)
    
    event_name = event.name
    try:
        db.session.delete(event)
        db.session.commit()
        flash(f"Спортивна подія '{event_name}' успішно видалена!", "success")
        logger.info(f"Sport event deleted: {event_name} by user {current_user.username}")
    except Exception as e:
        db.session.rollback()
        flash("Помилка при видаленні події. Спробуйте ще раз.", "error")
        logger.error(f"Error deleting sport event: {str(e)}")
    
    return redirect(url_for("sport_events_bp.events_list"))

