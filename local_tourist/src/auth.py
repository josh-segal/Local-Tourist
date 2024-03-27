import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        culture_score = request.form['cultureRange']
        historic_score = request.form['historicRange']
        food_score = request.form['foodRange']
        scenic_score = request.form['scenicRange']
        preferences = {
            "culture": culture_score,
            "history": historic_score,
            "food": food_score,
            "scenic": scenic_score
        }

        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        doc_ref = db.collection('users').document(username)
        doc = doc_ref.get()
        if error is None and not doc.exists:
            user_data = {
                "username": username,
                "password": generate_password_hash(password),
                "preferences": preferences
            }
            db.collection('users').document(username).set(user_data)
            return redirect(url_for("index"))
        else:
            error = f"User {username} is already registered."

        flash(error)
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        doc_ref = db.collection('users').document(username).get()
        doc = doc_ref.to_dict()

        if not doc:
            error = 'Incorrect username.'
        elif not check_password_hash(doc['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = doc['username']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    db = get_db()
    user_collection = db.collection('users')
    user_first = user_collection.limit(1).get()
    if not user_first:
        g.user = None
    elif user_id is None:
        g.user = None
    else:
        db = get_db()
        user_doc = db.collection('users').document(user_id).get()
        user = user_doc.to_dict()
        g.user = user.get('username')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
