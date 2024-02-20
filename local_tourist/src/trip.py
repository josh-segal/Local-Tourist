import json

from flask import (
    Blueprint, render_template
)
from googlemaps import distance_matrix

from .db import get_db
from .algorithms import tsp_attractions
import googlemaps

file = open('src/key.txt', 'r')
api_key = file.read()
file.close()
gmaps = googlemaps.Client(key=api_key)  # read in key.txt

bp = Blueprint('trip', __name__)


@bp.route('/map/<string:user_id>/<string:mode>')
def map(user_id, mode):
    # db = get_db()
    # attractions = db.execute(
    #     f'SELECT attractions.*, user_attractions_{user_id}.user_attraction_id '
    #     'FROM attractions '
    #     f'INNER JOIN user_attractions_{user_id} '
    #     f'ON attractions.attractionID = user_attractions_{user_id}.attraction_id'
    # ).fetchall()
    #

    db = get_db()
    attractions = db.collection('attractions').stream()
    attractions_list = []
    for attraction in attractions:
        attractions_list.append(attraction.to_dict())

    db = get_db()
    attractions = db.collection('users').document(user_id)
    plan_doc = attractions.get()
    plan_data = plan_doc.to_dict()
    plan = plan_data['plan']
    # attractions_list = []
    # for attraction in plan:
    #     attractions_list.append(attraction)
    # distance_matrix = []
    lat = 'latitude'
    lng = 'longitude'
    for i, orgn in enumerate(plan):
        distance_duration_row = []
        for j, dest in enumerate(plan):
            origin = (orgn[lat], orgn[lng])
            destination = (dest[lat], dest[lng])
            distance_duration = gmaps.distance_matrix(origin, destination, mode=mode)["rows"][0]["elements"][0]["distance"]["value"]
            distance_duration_row.append(distance_duration)
        distance_matrix.append(distance_duration_row)

    optimal_distance, optimal_path = tsp_attractions(distance_matrix)
    attractions_optimal_order = [plan[i] for i in optimal_path]

    return render_template('trip/map.html', path=optimal_path, attractions=attractions_optimal_order)
    # db = get_db()
    # attractions = db.collection('attractions').stream()
    # return render_template('list/index.html', attractions=attractions)
