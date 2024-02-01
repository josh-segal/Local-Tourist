import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, get_flashed_messages
)
from werkzeug.exceptions import abort

from tourist_guide_app.auth import login_required
from tourist_guide_app.db import get_db
from tourist_guide_app.algorithms import bubble_sort_attractions
import sys

bp = Blueprint('list', __name__)


@bp.route('/')
def index():
    if g.user is not None:
        db = get_db()
        attractions = db.execute(
            'SELECT * '
            ' FROM attractions '
            ' ORDER BY attractionID'
        ).fetchall()
        preferences = db.execute('''
        SELECT 
            json_extract(preferences, '$.culture') AS culture_score,
            json_extract(preferences, '$.history') AS historic_score,
            json_extract(preferences, '$.food') AS food_score,
            json_extract(preferences, '$.scenic') AS scenic_score
        FROM user
        ''').fetchall()

        user_preferences = []
        for row in preferences:
            user_preferences.append(int(row[0]))
        attractions_sorted = bubble_sort_attractions(attractions, user_preferences)

        return render_template('list/index.html', attractions=attractions_sorted)
    else:
        db = get_db()
        attractions = db.execute(
            'SELECT * '
            ' FROM attractions '
            ' ORDER BY attractionID'
        ).fetchall()
        return render_template('list/index.html', attractions=attractions)


@bp.route('/add_to_trip/<int:user_id>/<int:attraction_id>', methods=['POST'])
def add_to_trip(user_id, attraction_id):
    db = get_db()

    # Check if the user has an associated user_attractions table
    db.execute(
        f'CREATE TABLE IF NOT EXISTS user_attractions_{user_id} ( '
        'user_attraction_id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'attraction_id INTEGER, '
        'FOREIGN KEY (attraction_id) REFERENCES attractions(attractionID) '
        ')'
    )
    db.commit()

    # Add the attraction to the user's trip in the user_attractions table
    db.execute(
        f'INSERT INTO user_attractions_{user_id} (attraction_id) VALUES (?)',
        (attraction_id,)
    )
    db.commit()

    # flash('Attraction added to your trip successfully.')
    return redirect(url_for('index'))


@bp.route('/plan/<int:user_id>')
def plan(user_id):
    db = get_db()
    if user_plan_db_exists(user_id):
        attractions = db.execute(
            f'SELECT attractions.*, user_attractions_{user_id}.user_attraction_id '
            'FROM attractions '
            f'INNER JOIN user_attractions_{user_id} '
            f'ON attractions.attractionID = user_attractions_{user_id}.attraction_id'
        ).fetchall()

        if (db.execute(
                "SELECT user_attraction_id "
                f"FROM user_attractions_{user_id} "
                "WHERE attraction_id=?;", (f"{1}",)
        ).fetchone() is None):
            flash('You having nothing planned.')
            return render_template('list/plan.html')

        # implement sorting with geolocation here ?
        return render_template('list/plan.html', attractions=attractions)
    else:
        flash("You don't have a plan yet.")
        return redirect(url_for('index'))


@bp.route('/plan/<int:user_id>', methods=('POST',))
@login_required
def clear_plan(user_id):
    db = get_db()
    if user_plan_db_exists(user_id):
        db.execute(
            f'DROP TABLE user_attractions_{user_id} '
        )
        db.commit()
    return redirect(url_for('index'))


@bp.route('/plan/<int:user_id>/<int:user_attraction_id>', methods=('DELETE', 'POST'))
@login_required
def clear_single_plan(user_id, user_attraction_id):
    db = get_db()
    if user_plan_db_exists(user_id):
        db.execute(
            f'DELETE FROM user_attractions_{user_id} '
            f'WHERE user_attraction_id = {user_attraction_id} '
        )
        db.commit()
    return redirect(url_for('list.plan', user_id=user_id))


@bp.route('/rank/<int:user_id>')
def rank(user_id):
    db = get_db()

    if user_rank_db_exists(user_id):
        attractions = db.execute(
            f'SELECT attractions.*, user_attractions_rank_{user_id}.user_attraction_rank '
            'FROM attractions '
            f'INNER JOIN user_attractions_rank_{user_id} '
            f'ON attractions.attractionID = user_attractions_rank_{user_id}.attraction_id'
        ).fetchall()

        return render_template('list/rank.html', attractions=attractions)

    else:
        flash("You don't have any rankings yet.")
        return redirect(url_for('index'))


@bp.route('/add_to_rank/<int:user_id>/<int:attraction_id>', methods=['POST'])
def add_to_rank(user_id, attraction_id):
    user_attraction_rank = 1

    db = get_db()

    if user_rank_db_exists(user_id):

        if (db.execute(
                "SELECT attraction_id "
                f"FROM user_attractions_rank_{user_id} "
                "WHERE attraction_id=?;", (f"{attraction_id}",)
        ).fetchone() is not None):
            # Add the attraction to the user's trip in the user_attractions table
            db.execute(
                f'INSERT INTO user_attractions_rank_{user_id} (user_attraction_rank, attraction_id) VALUES (?, ?)',
                (user_attraction_rank, attraction_id,)
            )
            db.commit()

    else:
        db.execute(
            f'CREATE TABLE IF NOT EXISTS user_attractions_rank_{user_id} ( '
            f'temp_primary_key INTEGER PRIMARY KEY AUTOINCREMENT, '
            'user_attraction_rank INTEGER, '
            'attraction_id INTEGER, '
            'FOREIGN KEY (attraction_id) REFERENCES attractions(attractionID) '
            ')'
        )
    db.commit()

    # return redirect(url_for('list.add_to_rank', user_id=user_id, attractions=attractions))
    return redirect(url_for('index'))


@bp.route('/rank/<int:user_id>', methods=('POST',))
@login_required
def clear_rank(user_id):
    db = get_db()
    if user_rank_db_exists(user_id):
        db.execute(
            f'DROP TABLE user_attractions_rank_{user_id} '
        )
        db.commit()
    return redirect(url_for('index'))


@bp.route('/rank/<int:user_id>/<int:user_attraction_rank>', methods=('DELETE', 'POST'))
@login_required
def clear_single_rank(user_id, user_attraction_rank):
    db = get_db()
    if user_rank_db_exists(user_id):
        db.execute(
            f'DELETE FROM user_attractions_rank_{user_id} '
            f'WHERE user_attraction_rank = {user_attraction_rank} '
        )
        db.commit()
    return redirect(url_for('list.rank', user_id=user_id))


def user_plan_db_exists(user_id):
    db = get_db()
    if (db.execute(
            "SELECT name "
            "FROM sqlite_master "
            "WHERE type='table' "
            "AND name=?;", (f"user_attractions_{user_id}",)
    ).fetchone() is not None):
        return True
    return False


def user_rank_db_exists(user_id):
    db = get_db()
    if (db.execute(
            "SELECT name "
            "FROM sqlite_master "
            "WHERE type='table' "
            "AND name=?;", (f"user_attractions_rank_{user_id}",)
    ).fetchone() is not None):
        return True
    return False
