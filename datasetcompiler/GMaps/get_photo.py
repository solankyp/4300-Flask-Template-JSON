# functions to retrieve a photo from a google maps location

import os
import requests
import hashlib
import imghdr
from io import BytesIO

API_KEY = "AIzaSyCodf6mMiaogjR8legcJyz-2-hjVAYcyaM"

def get_photo(photo_reference):
    url = "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=" + photo_reference + "&key=" + API_KEY

    file_directory = "GMaps/photos/"
    file_name = photo_reference.encode('utf-8')
    hashed_file_name = hashlib.sha256(file_name).digest()
    hashed_file_name = hashed_file_name.hex()
    file_path = file_directory + "/" + hashed_file_name

    if (not os.path.exists(file_path + ".png")) and (not os.path.exists(file_path + ".jpeg")) and (not os.path.exists(file_path + ".webp")):

        response = requests.get(url)
        img = BytesIO(response.content)

        if not os.path.exists(file_directory):
            # Create the directory if it doesn't exist
            os.makedirs(file_directory)


        with open(file_path + "." + str(imghdr.what(img)), 'wb') as file:
            file.write(response.content)
        return response.content
    
    else:
        print("photo cached")
        binary = None
        if (os.path.exists(file_path + ".png")):
            with open(file_path + ".png", 'rb') as file:
                binary = file.read()
        elif (os.path.exists(file_path + ".jpeg")):
            with open(file_path + ".jpeg", 'rb') as file:
                binary = file.read()
        else:
            with open(file_path + ".webp", 'rb') as file:
                binary = file.read()
        return binary