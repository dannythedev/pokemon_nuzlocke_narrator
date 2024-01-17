import os
import re
from collections import OrderedDict

import requests
import base64
from PyQt5.QtGui import QPixmap
import json

POKEMON_DIR = 'sav/pokemon.json'
ENCOUNTER_DIR = 'sav/gen/encounters{}.json'


def is_json_empty(filename):
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                if not data:
                    # If JSON is empty, create the file
                    with open(filename, 'w') as new_file:
                        new_file.write('[]')
                    return True
                return False
        except json.JSONDecodeError:
            # Handle invalid JSON by creating a new file
            with open(filename, 'w') as new_file:
                new_file.write('{}')
            return True
    else:
        # If the file does not exist, create it
        with open(filename, 'w') as new_file:
            new_file.write('{}')
        return True


def base64_to_pixmap(base64_string):
    # Decode the Base64 string, removing the Base64 prefix if present
    image_data = base64.b64decode(base64_string.split(",")[-1])
    pixmap = QPixmap()
    pixmap.loadFromData(image_data)
    return pixmap


def convert_image_url_to_base64(url):
    try:
        # Fetch the image from URL
        response = requests.get(url)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code.

        # Convert the image data to a Base64 string
        base64_string = base64.b64encode(response.content).decode('utf-8')

        return "data:png/jpeg;base64," + base64_string
    except requests.RequestException as e:
        print(f"Error fetching image from URL: {e}")
        return None


def regexify(regex, data):
    """Extracts regex string from data string."""
    try:
        return re.findall(regex, str(data))[0]
    except:
        return


def calculate_level_averages(levels):
    cell_averages = []

    for level in levels:
        if '-' in level:
            start, end = map(int, level.split('-'))
            average = (start + end) / 2
        else:
            average = level

        if isinstance(average, (int, float)):
            cell_averages.append(average)
    if cell_averages:
        averages = sum(cell_averages)/len(cell_averages)
        return averages
    return 100


def average_level(route_data):
    total_levels = sum(route_data.values())
    num_pokemon = len(route_data.values())
    if num_pokemon == 0:
        return 0
    return total_levels / num_pokemon


# Function to sort routes by average level
def sort_routes_by_average(region_data):
    sorted_routes = sorted(region_data.items(), key=lambda x: average_level(x[1]))
    return OrderedDict(sorted_routes)

# Function to sort routes for each region in the Pokemon dictionary
def sort_routes_for_each_region(pokemon_dict):
    sorted_pokemon_dict = OrderedDict()
    for region, region_data in pokemon_dict.items():
        sorted_routes = sort_routes_by_average(region_data)
        sorted_pokemon_dict[region] = sorted_routes
    return OrderedDict(sorted_pokemon_dict)

