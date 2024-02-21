import json

import requests
import pprint


def nearby_search(location):
    file = open('src/key.txt', 'r')
    api_key = file.read()
    file.close()
    # Define the request payload
    payload = {
        "includedTypes": ["museum", "amusement_park", "zoo", "art_gallery", "aquarium", "bowling_alley",
                          "movie_theater", "night_club", "park"],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": 42.3601,
                    "longitude": -71.0589
                },
                "radius": 5000.0
            }
        }
    }

    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName, places.formattedAddress, places.geometry.location.lat, "
                            "places.geometry.location.lng"
    }

    # Define the URL
    # url = "https://places.googleapis.com/v1/places:searchNearby"
    if location == 'Leuven':
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json" \
              "?location=50.8823%2C-4.7138" \
              "&rankby=distance" \
              "&type=Entertainment and Recreation" \
              f"&key={api_key}"
    else:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json" \
              "?location=42.3601%2C-71.0589" \
              "&radius=1500" \
              "&type=Entertainment and Recreation" \
              f"&key={api_key}"

    # Send the POST request
    response = requests.post(url)
    # , json=payload, headers=headers
    # base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    #
    # # Define the parameters
    # params = {
    #     "location": "42.3601,-71.0589",  # Latitude and longitude of Boston, MA
    #     "radius": "10000",  # Search radius in meters
    #     "type": "tourist_attraction",  # Type of places to search for
    #     "key": "YOUR_API_KEY"  # Your Google Maps API key
    # }
    #
    # # Send the GET request
    # response = requests.get(base_url, params=params)

    # Check the response status
    if response.status_code == 200:
        # Parse and return the response JSON
        response_json = response.json()
        place_ids = []
        attractions_list = []
        for attraction in response_json.get('results', []):
            place_ids.append(attraction.get('place_id', {}))
            # print("attraction: " + attraction.get('place_id', {}))
        for place_id in place_ids:
            place_details_url = f"https://maps.googleapis.com/maps/api/place/details/json?key={api_key}&place_id={place_id}&fields=name,formatted_address,geometry"

            response = requests.get(place_details_url)
            attraction = {}
            if response.status_code == 200:
                place_details = response.json()
                attraction['name'] = place_details['result']['name']
                attraction['location'] = place_details['result']['formatted_address']
                attraction['lat'] = place_details['result']['geometry']['location']['lat']
                attraction['lng'] = place_details['result']['geometry']['location']['lng']
                attractions_list.append(attraction)
                pprint.pprint(place_details)

        return attractions_list
    else:
        print(f"Error: {response.status_code}")
        return None
