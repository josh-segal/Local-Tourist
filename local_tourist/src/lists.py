import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, get_flashed_messages
)
# from werkzeug.exceptions import abort

# from local_tourist.auth import login_required
# from local_tourist.db import get_db
# from local_tourist.algorithms import bubble_sort_attractions

from .auth import login_required
from .db import get_db
from .algorithms import bubble_sort_attractions

# import sys


bp = Blueprint('list', __name__)


@bp.route('/')
def index():
    # if g.user is not None:
    #     db = get_db()
    #     attractions = db.execute(
    #         'SELECT * '
    #         ' FROM attractions '
    #         ' ORDER BY attractionID'
    #     ).fetchall()
    #     preferences = db.execute('''
    #     SELECT
    #         json_extract(preferences, '$.culture') AS culture_score,
    #         json_extract(preferences, '$.history') AS historic_score,
    #         json_extract(preferences, '$.food') AS food_score,
    #         json_extract(preferences, '$.scenic') AS scenic_score
    #     FROM user
    #     ''').fetchall()
    #
    #     user_preferences = []
    #     for row in preferences:
    #         user_preferences.append(int(row[0]))
    #     attractions_sorted = bubble_sort_attractions(attractions, user_preferences)
    #
    #     return render_template('list/index.html', attractions=attractions_sorted)
    # else:
    #     db = get_db()
    #     attractions = db.execute(
    #         'SELECT * '
    #         ' FROM attractions '
    #         ' ORDER BY attractionID'
    #     ).fetchall()
    #     return render_template('list/index.html', attractions=attractions)
    db = get_db()
    # Reference the document in the "attractions" collection with ID "1"
    doc_ref = db.collection('attractions').document('1')

    # Get the document snapshot
    doc_snapshot = doc_ref.get()

    # Check if the document exists
    if doc_snapshot.exists:
        # Access the data and retrieve the value of the "name" field
        data = doc_snapshot.to_dict()
        if "name" in data:
            name = data["name"]
            return name
        else:
            return "The 'name' field does not exist in document 1."
    else:
        return "Document 1 does not exist."


@bp.route('/add_to_trip/<int:user_id>/<int:attraction_id>', methods=['POST'])
def add_to_trip(user_id, attraction_id):
    db = get_db()

    # Check if the user has an associated user_attractions table
    db.execute(
        'CREATE TABLE IF NOT EXISTS user_attractions_{} ( '
        'user_attraction_id INTEGER PRIMARY KEY AUTOINCREMENT, '
        'attraction_id INTEGER, '
        'FOREIGN KEY (attraction_id) REFERENCES attractions(attractionID) '
        ')'.format(user_id)
    )
    db.commit()

    # Add the attraction to the user's trip in the user_attractions table
    db.execute(
        'INSERT INTO user_attractions_{} (attraction_id) VALUES (?)'.format(user_id),
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
            'SELECT attractions.*, user_attractions_{user_id}.user_attraction_id '
            'FROM attractions '
            'INNER JOIN user_attractions_{user_id} '
            'ON attractions.attractionID = user_attractions_{user_id}.attraction_id'.format(user_id = user_id)
        ).fetchall()

        if (db.execute(
                "SELECT user_attraction_id "
                "FROM user_attractions_{user_id} "
                "WHERE user_attraction_id={attraction_id}".format(user_id=user_id, attraction_id=1)
        ).fetchone() is None):
            flash('You having nothing planned.')
            return render_template('list/plan.html')

        # implement sorting with geolocation here ?
        return render_template('list/plan.html', attractions=attractions)
    else:
        flash("You don't have a plan yet.")
        return redirect(url_for('index'))


@bp.route('/clear_plan/<int:user_id>', methods=('POST',))
@login_required
def clear_plan(user_id):
    db = get_db()
    if user_plan_db_exists(user_id):
        db.execute(
            'DROP TABLE user_attractions_{} '.format(user_id)
        )
        db.commit()
    return redirect(url_for('index'))


@bp.route('/clear_single_plan/<int:user_id>/<int:user_attraction_id>', methods=('POST',))
@login_required
def clear_single_plan(user_id, user_attraction_id):
    db = get_db()
    if user_plan_db_exists(user_id):
        db.execute(
            'DELETE FROM user_attractions_{user_id} '
            'WHERE user_attraction_id = {user_attraction_id} '.format(user_id=user_id, user_attraction_id=user_attraction_id)
        )
        db.commit()
    return redirect(url_for('list.plan', user_id=user_id))


@bp.route('/rank/<int:user_id>')
def rank(user_id):
    db = get_db()

    if user_rank_db_exists(user_id):
        attractions = db.execute(
            'SELECT attractions.*, user_attractions_rank_{user_id}.user_attraction_rank '
            'FROM attractions '
            'INNER JOIN user_attractions_rank_{user_id} '
            'ON attractions.attractionID = user_attractions_rank_{user_id}.attraction_id'.format(user_id = user_id)
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

        # if (db.execute(
        #         "SELECT attraction_id "
        #         "FROM user_attractions_rank_{user_id} "
        #         "WHERE user_attraction_id={user_attraction_id};".format(user_id = user_id, user_attraction_id = 1)
        # ).fetchone() is not None):
            # Add the attraction to the user's trip in the user_attractions table
            db.execute(
                f'INSERT INTO user_attractions_rank_{user_id} (user_attraction_rank, attraction_id) VALUES (?, ?)',
                (user_attraction_rank, attraction_id,)
            )
            db.commit()

    else:
        db.execute(
            'CREATE TABLE IF NOT EXISTS user_attractions_rank_{} ( '
            'temp_primary_key INTEGER PRIMARY KEY AUTOINCREMENT, '
            'user_attraction_rank INTEGER, '
            'attraction_id INTEGER, '
            'FOREIGN KEY (attraction_id) REFERENCES attractions(attractionID) '
            ')'.format(user_id)
        )
    db.commit()

    db.execute(
        f'INSERT INTO user_attractions_rank_{user_id} (user_attraction_rank, attraction_id) VALUES (?, ?)',
        (user_attraction_rank, attraction_id,)
    )
    db.commit()

    # return redirect(url_for('list.add_to_rank', user_id=user_id, attractions=attractions))
    return redirect(url_for('index'))


# @bp.route('/GET_rank/<int:user_id>/<list:ranked_list>/<int:attraction_id>', methods=['GET'])
# def GET_rank():
#     db = get_db()
#     to_rank = db.execute(
#         'SELECT name '
#         'FROM attractions '
#         'WHERE attractionID = {}'.format(attraction_id)
#     ).fetchone()
#
#     mid = len(ranked_list) // 2
#     return render_template('list/POST_rank.html', user_id=user_id, ranked_list=ranked_list, mid_index=mid, to_rank=to_rank)
#
# @bp.route('/POST_rank/<int:user_id>/<list:ranked_list/to_rank>', methods=['POST'])
# def POST_rank():
#     direction = request.form['direction']
#     if left > right:
#         ranked_list.insert(left, to_rank)
#         return redirect(url_for('list.rank', user_id=user_id))
#     else:
#         mid = (left + right) // 2
#
#         db = get_db()
#         mid_place = db.execute(
#             'SELECT name '
#             'FROM attractions '
#             'WHERE attractionID = {}'.format(mid)
#         ).fetchone()
#
#         if direction == mid_place:
#
#             ranked_list = ranked_list[:mid]
#         else:
#             ranked_list = ranked_list[mid:]
#         return redirect(url_for('list.GET_rank', user_id=user_id, ranked_list=ranked_list, left=left, right=right))



@bp.route('/clear_rank/<int:user_id>', methods=('POST',))
@login_required
def clear_rank(user_id):
    db = get_db()
    if user_rank_db_exists(user_id):
        db.execute(
            'DROP TABLE user_attractions_rank_{} '.format(user_id)
        )
        db.commit()
    return redirect(url_for('index'))


@bp.route('/clear_single_rank/<int:user_id>/<int:user_attraction_rank>', methods=('POST',))
@login_required
def clear_single_rank(user_id, user_attraction_rank):
    db = get_db()
    if user_rank_db_exists(user_id):
        db.execute(
            'DELETE FROM user_attractions_rank_{user_id} '
            'WHERE user_attraction_rank = {user_attraction_rank} '.format(user_id = user_id, user_attraction_rank = user_attraction_rank)
        )
        db.commit()
    return redirect(url_for('list.rank', user_id=user_id))


def user_plan_db_exists(user_id):
    db = get_db()
    if (db.execute(
            "SELECT name "
            "FROM sqlite_master "
            "WHERE type='table' "
            "AND name= '{}';".format("user_attractions_" + str(user_id))
    ).fetchone() is not None):
        return True
    return False


def user_rank_db_exists(user_id):
    db = get_db()
    if (db.execute('''            
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' 
        AND name= '{}';'''.format('user_attractions_rank_' + str(user_id))

    ).fetchone() is not None):
        return True
    return False
