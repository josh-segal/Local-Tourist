from flask import (
    Blueprint, render_template
)

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

    db = get_db()
    attractions = db.collection('users').document(user_id)
    plan_doc = attractions.get()
    plan_data = plan_doc.to_dict()
    plan = plan_data['plan']
    lat = 'latitude'
    lng = 'longitude'
    user_distance_matrix = []
    for i, orgn in enumerate(plan):
        distance_duration_row = []
        for j, dest in enumerate(plan):
            origin = (orgn[lat], orgn[lng])
            destination = (dest[lat], dest[lng])
            distance_duration = \
                gmaps.distance_matrix(origin, destination, mode=mode)["rows"][0]["elements"][0]["distance"]["value"]
            distance_duration_row.append(distance_duration)
        user_distance_matrix.append(distance_duration_row)

    optimal_distance, optimal_path = tsp_attractions(user_distance_matrix)
    attractions_optimal_order = [plan[i] for i in optimal_path]

    return render_template('trip/map.html', path=optimal_path, attractions=attractions_optimal_order)
