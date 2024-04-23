from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from threading import Thread, Lock
import csv
from bottle import template

# Read treatment centers data from CSV
centers = []
with open('treatment_centers.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        center_name = row['Name']
        center_street = row['Street']
        center_city = row['City']
        center_state = row['State']
        try:
            center_lat = float(row['Latitude'].strip())
            center_lon = float(row['Longitude'].strip())
            centers.append((center_name, center_street, center_city, center_state, center_lat, center_lon))
        except ValueError:
            print(f"Skipping center '{center_name}' due to invalid latitude or longitude")
            continue

# Function to convert user's location to latitude and longitude
def get_location(location_str):
    geolocator = Nominatim(user_agent="treatment_center_finder")
    location = geolocator.geocode(location_str)
    if location is None:
        raise ValueError("Location not found")
    return location.latitude, location.longitude

# Function to calculate distance between two locations
def calculate_distance(center_location, user_location):
    center_name, _, _, _, center_lat, center_lon = center_location
    center_coords = (center_lat, center_lon)
    distance = geodesic(center_coords, user_location).miles
    return center_name, distance

# Function to find nearby centers based on user's location
def find_nearby_centers(user_location):
    nearby_centers = []
    for center in centers:
        center_name, distance = calculate_distance(center, user_location)
        nearby_centers.append((center_name, distance))
    return nearby_centers

# A lock for thread synchronization
lock = Lock()

# Function to handle user input and find nearby centers
def handle_user_input(location_str):
    location_str = location_str.replace("+", " ")
    try:
        user_location = get_location(location_str)
        # Find nearby centers
        with lock:
            nearby_centers = find_nearby_centers(user_location)

        return [user_location, nearby_centers]
    except Exception as e:
        print(f"Error: {e}. Please try again.")



class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        response_code = 200
        self.send_response(response_code)
        self.end_headers()
        if parsed_path.path == "/location":
            name_of_place = parsed_path.query.replace('loc=', '')
            output = handle_user_input(name_of_place)
            nearest = output[0]
            latitude = nearest[0]
            longitude = nearest[1]

            self.wfile.write(bytes(template('location', loc=name_of_place, latitude=latitude, longitude=longitude, rest=list(output[1:])), 'utf-8'))
        else:
            self.wfile.write(bytes(template('index', path=self.path), 'utf-8'))


def run():
    server = ThreadingHTTPServer(('0.0.0.0', 4444), Handler)
    server.serve_forever()


if __name__ == '__main__':
    run()
