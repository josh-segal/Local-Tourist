import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, get_flashed_messages
)
from werkzeug.exceptions import abort

# from local_tourist.auth import login_required
# from local_tourist.db import get_db
# from local_tourist.algorithms import bubble_sort_attractions
# from local_tourist.algorithms import tsp_attractions

# from local_tourist.auth import login_required
from .db import get_db
# from local_tourist.algorithms import bubble_sort_attractions
from .algorithms import tsp_attractions
import sys
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
    # distance_matrix = []
    # lat = 'latitude'
    # lng = 'longitude'
    # for i, orgn in enumerate(attractions):
    #     distance_duration_row = []
    #     for j, dest in enumerate(attractions):
    #         origin = (orgn[lat], orgn[lng])
    #         destination = (dest[lat], dest[lng])
    #         distance_duration = \
    #         gmaps.distance_matrix(origin, destination, mode=mode)["rows"][0]["elements"][0]["distance"]["value"]
    #         distance_duration_row.append(distance_duration)
    #     distance_matrix.append(distance_duration_row)
    #
    # optimal_distance, optimal_path = tsp_attractions(distance_matrix)
    # attractions_optimal_order = [attractions[i] for i in optimal_path]
    #
    # return render_template('trip/map.html', path=optimal_path, attractions=attractions_optimal_order)
    db = get_db()
    attractions = db.collection('attractions').stream()
    return render_template('list/index.html', attractions=attractions)