from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from models import Review
from flask_login import login_required, current_user
from bleach import clean

bp = Blueprint('reviews', __name__, url_prefix='/reviews')

REVIEW_PARAMS = [
    'rating', 'text'
]

def params():
    return { p: request.form.get(p) for p in REVIEW_PARAMS }

@bp.route('/create_form/<int:book_id>')
@login_required
def create_form(book_id):
    try:
        if current_user.can_write_review(book_id):
            return render_template('reviews/create.html', book_id=book_id)
        else:
            flash('Вы уже писали рецензию на данную книгу','warning')
            return redirect(url_for('books.detailed', book_id=book_id))
    except:
        flash('Ошибка при отображении формы', 'danger')
        return redirect(url_for('books.detailed', book_id=book_id))


@bp.route('/delete/<int:review_id>', methods=['POST'])
@login_required
def delete(review_id):
    try:
        review = db.session.query(Review).filter(Review.id == review_id).scalar()
        if review.user_id == current_user.id:
            db.session.query(Review).filter(Review.id == review_id).delete()
            db.session.commit()
            flash('Рецензия удалена', 'success')
        else:
            flash('Вероятно, данная рецензия Вам не принадлежит','warning')
        return redirect(url_for('books.detailed', book_id=review.book_id))
    except:
        flash('Ошибка при удалении','danger')
        return redirect(url_for('books.detailed', book_id=review.book_id))
        
@bp.route('/create/<int:book_id>', methods=['POST'])
@login_required
def create(book_id):
    try:
        params_from_form = params()
        for param in params_from_form:
            param = clean(param)
            
        params_from_form['book_id'] = book_id
        params_from_form['user_id'] = current_user.id
        
        review = Review(**params_from_form)
        db.session.add(review)
        db.session.commit()
        flash('Рецензия добавлена', 'success')
        return redirect(url_for('books.detailed', book_id=book_id))
    except:
        flash('Ошибка при создании рецензии', 'danger')
        return redirect(url_for('reviews.create', book_id = book_id))
        


