import requests
import os

API_KEY = "" #ENTER API KEY

def remove_spaces(string):
    return string.replace(" ", "_").lower()

def fetch_response(city, location_type):
    query = location_type + " in " + city
    query = query.replace(" ", "%20") # unicode for space

    file_directory = "GMaps/cities/" + remove_spaces(city)
    file_path = file_directory + "/" + remove_spaces(location_type) + ".json"

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + query + "&key=" + API_KEY

    if not os.path.exists(file_path):

        response = requests.get(url)
        


        if not os.path.exists(file_directory):
            # Create the directory if it doesn't exist
            os.makedirs(file_directory)


        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
    
    else:
        print("Already fetched " + location_type + " in " + city)

fetch_response("New York City", "sights")

