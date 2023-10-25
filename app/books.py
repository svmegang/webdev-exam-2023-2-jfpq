from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db, app
from models import Book, Genre, Book_To_Genre, Cover, Review
from img_saver import ImgSaver
from flask_login import login_required
from auth import check_rights
from bleach import clean

import os

bp = Blueprint('books', __name__, url_prefix='/books')

BOOK_PARAMS = [
    'id', 'title', 'short_desc', 'year', 'publish', 'author', 'pages', 'cover_id'
]

def params():
    return { p: request.form.get(p) for p in BOOK_PARAMS }

@bp.route('/create_form')
@login_required
@check_rights('book_create')
def create_form():
    try:
        genres = db.session.execute(db.select(Genre)).scalars()
        return render_template('books/create.html',genres=genres)
    except:
        flash('Ошибка отображения формы', 'danger')
        return redirect(url_for('index'))

@bp.route('/create', methods=['POST'])
@login_required
@check_rights('book_create')
def create():
    try:
        file = request.files.get('cover')
        if file and file.filename:
            cover = ImgSaver(file).save()
        
        params_from_form = params()
        for param in params_from_form:
            param = clean(param)
              
        book = Book(**params_from_form)
        
        if file:
            book.cover_id = cover.id

        db.session.add(book)
        db.session.commit()

        genres_form = request.form.getlist("genre")

        for genre in genres_form:
            db.session.add(Book_To_Genre(book_id = book.id,genre_id = genre))
        db.session.commit()

        flash(f'Книга "{book.title}" добавлена', 'success')
        return redirect(url_for('index'))
    except:
        db.session.rollback()
        flash('Ошибка при добавлении', 'danger')
        return redirect(url_for('books.create'))


@bp.route('/detailed/<int:book_id>')
def detailed(book_id):
    try:
        book = db.session.execute(db.select(Book).filter(Book.id == book_id)).scalar()
        reviews = db.session.execute(db.select(Review).filter(Review.book_id == book_id)).scalars()

        return render_template('books/detailed.html', book=book, reviews=reviews)
    except:
        flash('Ошибка при отображении', 'danger')
        return redirect(url_for('index'))
@bp.route('/edit_form/<int:book_id>')
@login_required
@check_rights('book_edit')
def edit_form(book_id):
    try:
        book = db.session.execute(db.select(Book).filter(Book.id == book_id)).scalar()
        genres = db.session.execute(db.select(Genre)).scalars()
        selected_genres = db.session.execute(db.select(Book_To_Genre).filter(Book_To_Genre.book_id == book_id)).scalars()
        selected_genres_ids = []
        for genre in selected_genres:
            selected_genres_ids.append(genre.genre_id)
        return render_template('books/edit.html', book = book, selected_genres_ids=selected_genres_ids, genres=genres)
    except:
        flash('Ошибка при отображении формы изменения информации о книге', 'danger')
        return redirect(url_for('index'))

@bp.route('/edit/<int:book_id>', methods=['POST'])
@login_required
@check_rights('book_edit')
def edit(book_id):
    try:
        params_from_form = params()
        for param in params_from_form:
            param = clean(param)
            
        book = db.session.execute(db.select(Book).filter(Book.id == book_id)).scalar()
            
        params_from_form['id'] = book_id
        params_from_form['cover_id'] = book.cover_id
            
        db.session.query(Book).filter(Book.id == book_id).update({
            **params_from_form
        })

        db.session.query(Book_To_Genre).filter(Book_To_Genre.book_id == book_id).delete()
        
        db.session.commit()
        
        genres = request.form.getlist("genre")
        for genre in genres:
            db.session.add(Book_To_Genre(book_id = book.id,genre_id = genre))
        db.session.commit()

        
        flash(f'Информация о книге "{book.title}" изменена','success')
        return redirect(url_for('index'))
    except:
        flash('Ошибка при изменении информации о книге', 'danger')
        return redirect(url_for('books.edit_form', book_id = book_id))
          
@bp.route('/delete/<int:book_id>', methods=['POST'])
@login_required
@check_rights('book_delete')
def delete(book_id):
    try:
        book = db.session.execute(db.select(Book).filter(Book.id == book_id)).scalar()
        
        if Book.query.filter(Book.cover_id == book.cover_id).count() == 1:
            cover = db.session.execute(db.select(Cover).filter(Cover.id == book.cover_id)).scalar()
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], cover.storage_filename))
            db.session.query(Cover).filter(Cover.id == book.cover_id).delete()
                        
        db.session.query(Book).filter(Book.id == book_id).delete()
        db.session.commit()
        flash(f'Информация о книге "{book.title}" удалена', 'success')
        return redirect(url_for('index'))
    except:
        db.session.rollback()
        flash('Ошибка при удалении', 'danger')
        return redirect(url_for('books.detailed', book_id = book_id))

        



