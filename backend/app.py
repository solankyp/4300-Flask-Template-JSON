import json
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import re
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# ROOT_PATH for linking with all your files.
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, 'data.json')

# Assuming your JSON data is stored in a file named 'data.json'
with open(json_file_path, 'r') as file:
    data = json.load(file)

def preprocess_data(data):
    preprocessed_data = defaultdict(list)
    for city, categories in data.items():
        for category, details in categories.items():
            if category == "Eat": #Currently Food Only
                for activity, description in details.items():
                    name = activity
                    address = ""
                    tags = []

                    address_match = re.search(r'\b([A-Z][a-z]+\s(?:Street|Avenue|Road|Drive|Lane|Parkway|Boulevard|Way|Place))\b', description)
                    tags_match = re.findall(r'\b[A-Z][a-z]+\b', description)
                    if address_match:
                        address = address_match.group(0)
                    if tags_match:
                        tags = tags_match
                    preprocessed_data[city].append((name, address, tags))
    return preprocessed_data

def create_term_frequency_matrix(data):
    term_frequency_matrix = defaultdict(dict)
    for city, data in data.items():
        for name, address, tags in data:
            terms = re.findall(r'\w+', name.lower() + ' ' + address.lower() + ' ' + ' '.join(tags))
            for term in terms:
                if term not in term_frequency_matrix[city]:
                    term_frequency_matrix[city][term] = 1
                else:
                    term_frequency_matrix[city][term] += 1
    return term_frequency_matrix

def calculate_jaccard_similarity(query, data_term_frequency_matrix):
    query_terms = set(re.findall(r'\w+', query.lower()))
    similarities = {}
    for city, matrix in data_term_frequency_matrix.items():
        data_terms = set(matrix.keys())
        intersection = query_terms.intersection(data_terms)
        union = query_terms.union(data_terms)
        jaccard_similarity = len(intersection) / len(union)
        similarities[city] = jaccard_similarity
    return similarities

@app.route("/")
def home():
    return render_template('base.html', title="sample html")

@app.route("/food_search")
def food_search():
    query = request.args.get("query")
    preprocessed_data = preprocess_data(data)

    term_frequency_matrix = create_term_frequency_matrix(preprocessed_data)
    similarities = calculate_jaccard_similarity(query, term_frequency_matrix)
    return jsonify(similarities)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)