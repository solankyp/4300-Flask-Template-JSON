### merge GMaps and Wikitravel directories into city-keyed json

import os
import json
import sys
sys.path.insert(0, "/Users/maximiliandittgen/Documents/Projects/Landmark Parser/GMaps")
import get_photo as gp
import base64
from PIL import Image
import io
from io import BytesIO


# create final dict
dataset = {}

wikitravel_json = 'WikiTravel/dataset.json'
gmaps_directory = "GMaps/cities"

# Open the JSON file and load its contents into a dictionary
with open(wikitravel_json, 'r') as file:
    wikitravel_data = json.load(file)

for idx, city in enumerate(list(wikitravel_data.keys())):
    # if idx > 50: # for sample submission
    #     break
    # parse out wikitravel
    dataset[city] = {}
    dataset[city]["wikitravel"] = {}
    dataset[city]["gmaps"] = {}
    for topic in (list(wikitravel_data[city].keys())):
        dataset[city]["wikitravel"][topic] = wikitravel_data[city][topic]
    
        path = os.path.join(gmaps_directory, city.replace(" ","_").lower())
        # Check if the entry is a directory
        if os.path.isdir(path):
            for filename in os.listdir(path):
                # get json name
                topic = filename[:-5]
                dataset[city]["gmaps"][topic] = {}
                file_path = os.path.join(path, filename)
                with open(file_path, 'r') as file:
                    data = json.load(file)
                    locations = data["results"]
                    for loc_idx, location in enumerate(locations):
                        name = location["name"]
                        dataset[city]["gmaps"][topic][name] = {}
                        dataset[city]["gmaps"][topic][name]["name"] = name
                        
                        ## attributes
                        dataset[city]["gmaps"][topic][name]["coordinates"] = location["geometry"]["location"]
                        dataset[city]["gmaps"][topic][name]["address"] = location["formatted_address"]
                        if "rating" in list(location.keys()):
                            dataset[city]["gmaps"][topic][name]["rating"] = location["rating"]
                            dataset[city]["gmaps"][topic][name]["nratings"] = location["user_ratings_total"]
                        dataset[city]["gmaps"][topic][name]["tags"] = location["types"]

                        # if loc_idx < 4 and "photos" in list(location.keys()):
                        #     dataset[city]["gmaps"][topic][name]["photo"] = {}
                        #     dataset[city]["gmaps"][topic][name]["photo"]["photo_reference"] = location["photos"][0]["photo_reference"]
                        #     print("Grabbing photo from a " + str(city) + " " + str(topic))
                        #     with Image.open(io.BytesIO(gp.get_photo(location["photos"][0]["photo_reference"]))) as img:
                        #         resized = img.resize((int(img.width * 0.7), int(img.height * 0.7)), resample=Image.BILINEAR)
                        #         resized_rgb = resized.convert('RGB')
                        #         buffered = BytesIO()
                        #         resized_rgb.save(buffered, format="JPEG", quality = 90, optimize=True)
                        #         img_str = base64.b64encode(buffered.getvalue())
                        #         dataset[city]["gmaps"][topic][name]["photo"]["photo_binary"] = img_str.decode('utf-8')
        else:
            print("couldn't find gmaps directory for " + str(city))

with open("merged_data_without_photos.json", 'w', encoding='utf-8') as file:
    json.dump(dataset, file)

