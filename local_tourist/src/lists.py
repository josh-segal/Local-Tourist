import json

from firebase_admin import firestore as firebase
from flask import (
    Blueprint, flash, g, redirect, render_template, url_for, session
)

from .auth import login_required
from .db import get_db
from .algorithms import bubble_sort_attractions
from .googlemaps_places import nearby_search

file = open('src/key.txt', 'r')
api_key = file.read()
file.close()

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
        return render_template('list/index.html', attractions=attractions, api_key=api_key)
    else:
        db = get_db()
        attractions = db.collection('attractions').stream()
    return render_template('list/index.html', attractions=attractions, api_key=api_key)


@bp.route('/location/<string:location>', methods=['POST', ])
def change_location(location):
    session['location'] = location
    user_id = g.user
    clear_plan(user_id)
    flash('Location changed to ' + location)
    return redirect(url_for('index', api_key=api_key))


# TODO: ADD UNIQUE IDS TO ATTRACTIONS LOOK AT INDEX.HTML ROUTING
@bp.route(
    '/add_to_trip/<string:user_id>/<string:attraction_id>/<string:name>/<string:location>/<string:lat>/<string:lng'
    '>/<string:photo_ref>',
    methods=['POST'])
def add_to_trip(user_id, attraction_id, name, location, lat, lng, photo_ref):
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
            'photo_ref': photo_ref,
        }

        doc_ref.set(data)

        user_doc_ref = db.collection('users').document(user_id)
        new_attraction = doc_ref
        attraction = new_attraction.get().to_dict()
        current_plan = user_doc_ref.get().to_dict().get('plan', [])
        new_plan = current_plan + [attraction]
        user_doc_ref.update({'plan': new_plan})

    flash('Attraction added to your trip successfully.')
    return redirect(url_for('index', api_key=api_key))


@bp.route('/plan/<string:user_id>')
def plan(user_id):
    db = get_db()
    if user_plan_db_exists(user_id):
        attractions = db.collection('users').document(user_id)
        plan_doc = attractions.get()
        plan = plan_doc.get('plan')
        # implement sorting with geolocation here ?
        return render_template('list/plan.html', attractions=plan, api_key=api_key)
    else:
        flash("You don't have a plan yet.")
    return redirect(url_for('index', api_key=api_key))


@bp.route('/clear_plan/<string:user_id>', methods=('POST',))
def clear_plan(user_id):
    db = get_db()
    doc_ref = db.collection('users').document(user_id)
    doc_ref.update({'plan': firebase.firestore.DELETE_FIELD})
    return redirect(url_for('index', api_key=api_key))


@bp.route('/clear_single_plan/<string:user_id>/<string:user_attraction_id>', methods=('POST',))
@login_required
def clear_single_plan(user_id, user_attraction_id):
    db = get_db()
    doc_ref = db.collection('users').document(user_id)
    target_doc_ref = db.collection('attractions').document(user_attraction_id).get().to_dict()
    doc_ref.update({'plan': firebase.firestore.ArrayRemove([target_doc_ref])})
    return redirect(url_for('list.plan', user_id=user_id, api_key=api_key))


@bp.route('/rank/<string:user_id>')
def rank(user_id):
    db = get_db()

    if user_rank_db_exists(user_id):
        attractions = db.collection('users').document(user_id)
        rank_doc = attractions.get()
        rank = rank_doc.get('rank')
        return render_template('list/rank.html', attractions=rank, api_key=api_key)

    else:
        flash("You don't have any rankings yet.")
    return redirect(url_for('index', api_key=api_key))


@bp.route('/add_to_rank/<string:user_id>/<string:attraction_id>/<string:name>/<string:location>/<string:lat>/<string'
          ':lng>/<string:photo_ref>', methods=['GET', 'POST', ])
def add_to_rank(user_id, attraction_id, name, location, lat, lng, photo_ref):
    db = get_db()
    user_doc_ref = db.collection('users').document(user_id)
    data = {
        'name': name,
        'location': location,
        'latitude': float(lat),
        'longitude': float(lng),
        'id': attraction_id,
        'rank': 1,
        'photo_ref': photo_ref,
    }
    if user_rank_db_exists(user_id):
        current_plan = user_doc_ref.get().to_dict().get('rank', [])
        n = len(current_plan)
        if n == 0:
            new_plan = current_plan + [data]
            user_doc_ref.update({'rank': new_plan})
        else:
            if n // 2 == 0:
                first_zero_comp = 1
            else:
                first_zero_comp = 0

            return redirect(
                url_for('list.GET_rank', user_id=user_id, attraction_id=attraction_id, name=name, location=location,
                        lat=lat, lng=lng, leftIdx=0, rightIdx=n, first_zero_comp=first_zero_comp, api_key=api_key))
    else:
        user_doc_ref.update({'rank': [data]})

    flash('Attraction added to your ranking successfully.')
    return redirect(url_for('index', api_key=api_key))


@bp.route('/GET_rank/<string:user_id>/<string:attraction_id>/<string:name>/<string:location>/<string:lat>/<string'
          ':lng>/<int:leftIdx>/<int:rightIdx>/<int:first_zero_comp>', methods=['GET', 'POST'])
def GET_rank(user_id, attraction_id, name, location, lat, lng, leftIdx, rightIdx, first_zero_comp):

    db = get_db()
    attractions = db.collection('users').document(user_id)
    rank_doc = attractions.get().to_dict()
    ranked_list = rank_doc.get('rank')
    mid = (leftIdx + rightIdx) // 2
    data = {
        'name': name,
        'location': location,
        'latitude': float(lat),
        'longitude': float(lng),
        'id': attraction_id,
        'rank': leftIdx
    }

    if leftIdx == mid == 0:
        # print("swapping")
        # print("zero before: ", first_zero_comp)
        if first_zero_comp == 1:
            # print("swapping to 0")
            first_zero_comp = 0
        else:
            # print("swapping to 1")
            first_zero_comp = 1
    print("zero after: ", first_zero_comp)
    print("mid: ", mid)
    print("left: ", leftIdx)
    print("right: ", rightIdx)
    print("zero: ", first_zero_comp)

    if leftIdx >= rightIdx:
        new_ranked_list = ranked_list[:leftIdx] + [data] + ranked_list[leftIdx:]
        attractions.update({'rank': new_ranked_list})
        return redirect(url_for('list.rank', user_id=user_id, api_key=api_key))

    elif leftIdx == mid and not first_zero_comp and len(ranked_list) > 1:
        # Insert data at leftIdx
        new_ranked_list = ranked_list[:rightIdx] + [data] + ranked_list[rightIdx:]
        attractions.update({'rank': new_ranked_list})
        return redirect(url_for('list.rank', user_id=user_id, api_key=api_key))

    elif leftIdx == mid and first_zero_comp and len(ranked_list) == 1:
        new_ranked_list = ranked_list[:rightIdx] + [data] + ranked_list[rightIdx:]
        attractions.update({'rank': new_ranked_list})
        return redirect(url_for('list.rank', user_id=user_id, api_key=api_key))

    elif rightIdx == mid:
        # Insert data at rightIdx
        new_ranked_list = ranked_list[:rightIdx] + [data] + ranked_list[rightIdx:]
        attractions.update({'rank': new_ranked_list})
        return redirect(url_for('list.rank', user_id=user_id, api_key=api_key))
    else:

        return render_template('list/GET_rank.html', ranked_list=ranked_list, user_id=user_id, leftIdx=leftIdx,
                               rightIdx=rightIdx, attraction_id=attraction_id, name=name, location=location,
                               lat=lat, lng=lng, first_zero_comp=first_zero_comp, api_key=api_key)


@bp.route('/clear_rank/<string:user_id>', methods=('POST',))
@login_required
def clear_rank(user_id):
    db = get_db()
    doc_ref = db.collection('users').document(user_id)
    doc_ref.update({'rank': firebase.firestore.DELETE_FIELD})
    return redirect(url_for('index', api_key=api_key))


@bp.route('/clear_single_rank/<string:user_id>/<int:to_remove>', methods=('POST',))
@login_required
def clear_single_rank(user_id, to_remove):
    db = get_db()
    attractions = db.collection('users').document(user_id)
    rank_doc = attractions.get().to_dict()
    ranked_list = rank_doc.get('rank')

    print("index: ", to_remove)
    print("len list: ", len(ranked_list))

    if 0 <= to_remove < len(ranked_list):
        if to_remove == len(ranked_list) - 1:
            new_ranked_list = ranked_list[:to_remove]
        else:
            new_ranked_list = ranked_list[:to_remove] + ranked_list[(to_remove + 1):]
        attractions.update({'rank': new_ranked_list})

    return redirect(url_for('list.rank', user_id=user_id, api_key=api_key))


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