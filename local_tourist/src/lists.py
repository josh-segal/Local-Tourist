import json

from firebase_admin import firestore as firebase
from flask import (
    Blueprint, flash, g, redirect, render_template, url_for, session
)

from .auth import login_required
from .db import get_db
from .algorithms import bubble_sort_attractions
from .googlemaps_places import nearby_search

bp = Blueprint('list', __name__)


@bp.route('/')
def index():
    if 'location' not in session:
        session['location'] = "Boston"
    if g.user is not None:
        db = get_db()
        location = session['location']
        attractions = nearby_search(location)
        preferences = db.collection('users').document(g.user)
        pref_doc = preferences.get()
        pref = pref_doc.get('preferences')
        user_preferences = []
        for key, value in pref.items():
            user_preferences.append(value)
        # attractions_sorted = bubble_sort_attractions(attractions_list, user_preferences) TODO: reimplement user pref model with new places data points
        # return render_template('list/index.html', attractions=attractions_sorted)
        return render_template('list/index.html', attractions=attractions)
    else:
        db = get_db()
        attractions = db.collection('attractions').stream()
    return render_template('list/index.html', attractions=attractions)


@bp.route('/location/<string:location>', methods=['POST', ])
def change_location(location):
    session['location'] = location
    flash('Location changed to ' + location)
    return redirect(url_for('index'))


# TODO: ADD UNIQUE IDS TO ATTRACTIONS LOOK AT INDEX.HTML ROUTING
@bp.route(
    '/add_to_trip/<string:user_id>/<string:attraction_id>/<string:name>/<string:location>/<string:lat>/<string:lng>',
    methods=['POST'])
def add_to_trip(user_id, attraction_id, name, location, lat, lng):
    db = get_db()
    collection_ref = db.collection('attractions')
    doc_ref = collection_ref.document(attraction_id)
    doc = doc_ref.get()

    if doc.exists:
        user_doc_ref = db.collection('users').document(user_id)
        attraction = doc.to_dict()
        current_plan = user_doc_ref.get().to_dict().get('plan', [])
        new_plan = current_plan + [attraction]
        user_doc_ref.update({'plan': new_plan})

    else:
        data = {
            'name': name,
            'location': location,
            'latitude': float(lat),
            'longitude': float(lng),
            'id': attraction_id,
        }

        doc_ref = db.collection('attractions').document(attraction_id)
        doc_ref.set(data)

        user_doc_ref = db.collection('users').document(user_id)
        new_attraction = collection_ref.document(attraction_id)
        attraction = new_attraction.get().to_dict()
        current_plan = user_doc_ref.get().to_dict().get('plan', [])
        new_plan = current_plan + [attraction]
        user_doc_ref.update({'plan': new_plan})

    flash('Attraction added to your trip successfully.')
    return redirect(url_for('index'))


@bp.route('/plan/<string:user_id>')
def plan(user_id):
    db = get_db()
    if user_plan_db_exists(user_id):
        attractions = db.collection('users').document(user_id)
        plan_doc = attractions.get()
        plan = plan_doc.get('plan')
        # implement sorting with geolocation here ?
        return render_template('list/plan.html', attractions=plan)
    else:
        flash("You don't have a plan yet.")
    return redirect(url_for('index'))


@bp.route('/clear_plan/<string:user_id>', methods=('POST',))
@login_required
def clear_plan(user_id):
    db = get_db()
    doc_ref = db.collection('users').document(user_id)
    doc_ref.update({'plan': firebase.firestore.DELETE_FIELD})
    return redirect(url_for('index'))


@bp.route('/clear_single_plan/<string:user_id>/<string:user_attraction_id>', methods=('POST',))
@login_required
def clear_single_plan(user_id, user_attraction_id):
    db = get_db()
    doc_ref = db.collection('users').document(user_id)
    target_doc_ref = db.collection('attractions').document(user_attraction_id).get().to_dict()
    doc_ref.update({'plan': firebase.firestore.ArrayRemove([target_doc_ref])})
    return redirect(url_for('list.plan', user_id=user_id))


@bp.route('/rank/<string:user_id>')
def rank(user_id):
    db = get_db()

    if user_rank_db_exists(user_id):
        attractions = db.collection('users').document(user_id).get().get('rank')
        attractions_list = []
        for attraction in attractions:
            attractions_list.append(attraction.get().to_dict())
        return render_template('list/rank.html', attractions=attractions_list)

    else:
        flash("You don't have any rankings yet.")
    return redirect(url_for('index'))


@bp.route('/add_to_rank/<string:user_id>/<string:attraction_id>', methods=['POST'])
def add_to_rank(user_id, attraction_id):
    user_attraction_rank = 1  # TODO: rank implementation needed here

    db = get_db()
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get().to_dict()
    target_doc_ref = db.collection('attractions').document(attraction_id)
    if user_rank_db_exists(user_id):
        new_field_data = {
            user_attraction_rank: target_doc_ref
        }
        doc.update({
            'rank': firebase.firestore.ArrayUnion([new_field_data])
        })
    else:
        array_data = [target_doc_ref]
        doc_ref.update({
            'rank': array_data
        })

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


@bp.route('/clear_rank/<string:user_id>', methods=('POST',))
@login_required
def clear_rank(user_id):
    db = get_db()
    doc_ref = db.collection('users').document(user_id)
    doc_ref.update({'rank': firebase.firestore.DELETE_FIELD})
    return redirect(url_for('index'))


@bp.route('/clear_single_rank/<string:user_id>/<string:user_attraction_rank>', methods=('POST',))
@login_required
def clear_single_rank(user_id, user_attraction_rank):
    db = get_db()
    doc_ref = db.collection('users').document(user_id)
    target_doc_ref = db.collection('attractions').document(user_attraction_rank)
    doc_ref.update({'rank': firebase.firestore.ArrayRemove([target_doc_ref])})
    return redirect(url_for('list.rank', user_id=user_id))


def user_plan_db_exists(user_id):
    db = get_db()
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    doc_data = doc.to_dict()
    if 'plan' in doc_data:
        return True
    return False


def user_rank_db_exists(user_id):
    db = get_db()
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    doc_data = doc.to_dict()
    if 'rank' in doc_data:
        return True
    return False
