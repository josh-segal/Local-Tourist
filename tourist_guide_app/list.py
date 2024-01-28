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
        # user_preferences = {
        #     "culture": 1,
        #     "history": 1,
        #     "food": 5,
        #     "scenic": 1,
        # }
        attractions_sorted = bubble_sort_attractions(attractions, user_preferences)

        print(preferences, file=sys.stdout)
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
        f'CREATE TABLE IF NOT EXISTS user_attractions_{user_id} ('
        'user_attraction_id INTEGER PRIMARY KEY AUTOINCREMENT,'
        'attraction_id INTEGER,'
        'FOREIGN KEY (attraction_id) REFERENCES attractions(attractionID)'  
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
    attractions = db.execute(
        'SELECT * '
        'FROM attractions '
        f'INNER JOIN user_attractions_{user_id} '
        f'ON attractions.attractionID = user_attractions_{user_id}.attraction_id'
    ).fetchall()
    #implement sorting with geolocation here ?
    return render_template('list/plan.html', attractions=attractions)


@bp.route('/plan/<int:user_id>', methods=('POST',))
@login_required
def clear(user_id):
    db = get_db()
    db.execute(
        f'DROP TABLE user_attractions_{user_id} '
    )
    db.commit()
    return redirect(url_for('index'))
