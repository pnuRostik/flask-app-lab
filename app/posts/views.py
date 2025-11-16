"""CRUD-маршрути"""
from flask import render_template, redirect, url_for, flash, request, session
from . import posts_bp
from .models import Post, Tag
from .forms import PostForm
from app import db
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import joinedload

@posts_bp.route('/post')
def posts_list():
    """Відображення списку всіх видимих постів за датою публікації (спадання)"""
    stmt = (
        select(Post)
        .where(Post.is_active == True)
        .options(joinedload(Post.user))
        .order_by(Post.posted.desc())
    )
    posts = db.session.scalars(stmt).unique().all()
    return render_template('posts/posts.html', posts=posts)


@posts_bp.route('/post/<int:id>')
def post_detail(id):
    """Перегляд конкретного поста"""
    stmt = (
        select(Post)
        .where(Post.id == id)
        .options(joinedload(Post.user), joinedload(Post.tags))
    )
    post = db.session.scalar(stmt)
    if not post:
        flash('Пост не знайдено', 'error')
        return redirect(url_for('posts_bp.posts_list'))
    if not post.is_active:
        flash('Пост не знайдено', 'error')
        return redirect(url_for('posts_bp.posts_list'))
    return render_template('posts/detail_post.html', post=post)


@posts_bp.route('/post/create', methods=['GET', 'POST'])
def create_post():
    """Створення нового поста"""
    form = PostForm()

    if form.validate_on_submit():
        # Обробляємо дату публікації (конвертуємо з рядка datetime-local в datetime об'єкт)
        if form.publish_date.data:
            try:
                publish_date = datetime.strptime(form.publish_date.data, '%Y-%m-%dT%H:%M')
            except (ValueError, TypeError):
                publish_date = datetime.utcnow()
        else:
            publish_date = datetime.utcnow()
        
        post = Post(
            title=form.title.data,
            content=form.content.data,
            is_active=form.enabled.data if form.enabled.data is not None else True,
            posted=publish_date,
            category=form.category.data,
            user_id=form.author_id.data
        )
        
        # Обробляємо теги
        if form.tags.data:
            tag_ids = [int(tag_id) for tag_id in form.tags.data if tag_id]
            tags = db.session.scalars(select(Tag).where(Tag.id.in_(tag_ids))).all()
            post.tags = tags
        
        try:
            db.session.add(post)
            db.session.commit()
            flash('Post added successfully', 'success')
            return redirect(url_for('posts_bp.post_detail', id=post.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Помилка при створенні поста: {str(e)}', 'error')
    
    return render_template('posts/add_post.html', form=form)


@posts_bp.route('/post/<int:id>/update', methods=['GET', 'POST'])
def update_post(id):
    """Редагування поста"""
    stmt = (
        select(Post)
        .where(Post.id == id)
        .options(joinedload(Post.user), joinedload(Post.tags))
    )
    post = db.session.scalar(stmt)
    if not post:
        flash('Пост не знайдено', 'error')
        return redirect(url_for('posts_bp.posts_list'))
    form = PostForm(obj=post)
    
    if request.method == 'GET':
        if post.posted:
            form.publish_date.data = post.posted.strftime('%Y-%m-%dT%H:%M')
        form.enabled.data = post.is_active
        form.author_id.data = post.user_id  # Встановлюємо поточного автора
        # Встановлюємо поточні теги
        if post.tags:
            form.tags.data = [str(tag.id) for tag in post.tags]
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.is_active = form.enabled.data if form.enabled.data is not None else True
        post.user_id = form.author_id.data  # Оновлюємо автора
        
        if form.publish_date.data:
            try:
                post.posted = datetime.strptime(form.publish_date.data, '%Y-%m-%dT%H:%M')
            except (ValueError, TypeError):
                pass  
        
        post.category = form.category.data
        
        # Оновлюємо теги
        if form.tags.data:
            tag_ids = [int(tag_id) for tag_id in form.tags.data if tag_id]
            tags = db.session.scalars(select(Tag).where(Tag.id.in_(tag_ids))).all()
            post.tags = tags
        else:
            post.tags = []
        
        try:
            db.session.commit()
            flash('Пост успішно оновлено!', 'success')
            return redirect(url_for('posts_bp.post_detail', id=post.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Помилка при оновленні поста: {str(e)}', 'error')
    
    return render_template('posts/add_post.html', form=form, post=post)


@posts_bp.route('/post/<int:id>/delete', methods=['GET', 'POST'])
def delete_post(id):
    """Видалення поста - GET для підтвердження, POST для видалення"""
    post = db.get_or_404(Post, id)
    
    if request.method == 'POST':
        try:
            db.session.delete(post)
            db.session.commit()
            flash('Пост успішно видалено!', 'success')
            return redirect(url_for('posts_bp.posts_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Помилка при видаленні поста: {str(e)}', 'error')
            return redirect(url_for('posts_bp.post_detail', id=post.id))
    
    # GET - показуємо сторінку підтвердження
    return render_template('posts/delete_confirm.html', post=post)
