from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User
from app import db as db
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/auth')


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Необходимо выполнить вход'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)

def load_user(user_id):
    user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar()
    return user

@bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            login = request.form.get('login')
            password = request.form.get('password')
            remember_me = request.form.get('remember_me')
            if remember_me == 'on':
                remember_me = True
            else:
                remember_me = False
            print(remember_me)
            print('--------------')
            if login and password:
                user = db.session.execute(db.select(User).filter_by(login=login)).scalar()
                if user and user.check_password(password):
                    login_user(user, remember=remember_me)
                    flash('Вход выполнен успешно', 'success')
                    next = request.args.get('next')
                    return redirect(url_for('index') or next)
            flash('Пользователь с такими данными не найден', 'danger')
            return redirect(url_for('auth.login'))
        if request.method == 'GET':
            return render_template('auth/login.html')
    except:
        flash('Ошибка при загрузке', 'danger')
        return redirect(url_for('index'))

@bp.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        return redirect(url_for('index'))
    except:
        flash('Ошибка. Попробуйте позже', 'danger')
        return redirect(url_for('index'))

def check_rights(action):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = None
            user_id = kwargs.get("user_id")
            if user_id:
                user = load_user(user_id)
            if not current_user.can(action, user):
                flash("Недостаточно прав", "warning")
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator
