import googlemaps
import pprint


def nearby_search(location):
    file = open('src/key.txt', 'r')
    api_key = file.read()
    file.close()

    client = googlemaps.Client(api_key)

    if location == "Leuven":
        place = client.places_nearby(location="50.8476,4.3572", radius="1500", type="museum")
    else:
        place = client.places_nearby(location="42.3601,-71.0589", radius="1500", type="museum")

    all_places = place["results"]

    pprint.pprint(all_places)
    return all_places
