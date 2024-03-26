import json
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import re
from collections import defaultdict
import math

app = Flask(__name__)
CORS(app)

# ROOT_PATH for linking with all your files.
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, 'data.json')

# Assuming your JSON data is stored in a file named 'data.json'
with open(json_file_path, 'r') as file:
    data = json.load(file)

def preprocess_data(data):
    preprocessed_data = defaultdict(str)
    for city, categories in data.items():
        for _, details in categories.items():
            food_info = details.get('Eat')
            if food_info is not None:
                preprocessed_data[city] = food_info
    return preprocessed_data

def create_term_frequency_matrix(data):
    term_frequency_matrix = defaultdict(dict)
    for city, food_info in data.items():
        terms = re.findall(r'\w+', food_info.lower())
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

def top_sim(similarities):
    sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
    top_10 = sorted_similarities[:10]
    return top_10

def calculate_query_vector(query, data_term_frequency_matrix):
    query_vector = defaultdict(int)
    terms = re.findall(r'\w+', query.lower())
    for term in terms:
        query_vector[term] += 1
    return query_vector

def calculate_cosine_similarity(query_vector, doc_vector):
    dotprod = 0
    for term in query_vector:
        prod = query_vector.get(term,0)*doc_vector.get(term,0)
        dotprod+=prod
    query_sum = 0
    doc_sum = 0
    for value in query_vector.values():
        query_sum += (value**2)
    for value in query_vector.values():
        doc_sum += (value**2)

    query_norm = math.sqrt(query_sum)
    doc_norm = math.sqrt(doc_sum)

    if query_norm==0 or doc_norm==0:
        return 0
    cossim = dotprod / (query_norm*doc_norm)
    return cossim

@app.route("/")
def home():
    return render_template('base.html', title="Sample HTML")

@app.route("/food_search")
def food_search():
    query = request.args.get("query")
    preprocessed_data = preprocess_data(data)
    term_frequency_matrix = create_term_frequency_matrix(preprocessed_data)
    # similarities = calculate_jaccard_similarity(query, term_frequency_matrix)

    query_vector = calculate_query_vector(query, term_frequency_matrix)
    similarities = {}
    for city, city_vector in term_frequency_matrix.items():
        cosine_sim = calculate_cosine_similarity(query_vector, city_vector)
        similarities[city] = cosine_sim


    top_10 = top_sim(similarities)
    
    top_10_json = [{"city": city, "similarity": similarity} for city, similarity in top_10]
    return jsonify(top_10=top_10_json)


if __name__ == "__main__":
    app.run(debug=True)