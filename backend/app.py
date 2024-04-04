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

with open(json_file_path, 'r') as file:
    data = json.load(file)

def preprocess_data(data):
    preprocessed_data = defaultdict(dict) 
    for city, categories in data.items():
        for _, details in categories.items():
            food_info = details.get('Eat')
            activities = details.get('Do')
            buy = details.get('Buy')
            if food_info is not None:
                preprocessed_data[city]['Eat'] = food_info 
            if activities is not None:
                preprocessed_data[city]['Do'] = activities
            if buy is not None:
                preprocessed_data[city]['Buy'] = buy
    return preprocessed_data

def create_term_frequency_matrix(data):
    term_frequency_matrix = defaultdict(dict)
    for city, city_data in data.items():
        for category in city_data.keys():
            info = city_data.get(category)
            terms = re.findall(r'\w+', info.lower())
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
        prod = query_vector.get(term, 0) * doc_vector.get(term, 0)
        dotprod += prod

    query_sum = sum(value ** 2 for value in query_vector.values())
    doc_sum = sum(value ** 2 for value in doc_vector.values())

    query_norm = math.sqrt(query_sum)
    doc_norm = math.sqrt(doc_sum)

    if query_norm == 0 or doc_norm == 0:
        return 0

    cossim = dotprod / (query_norm * doc_norm)
    normalized_cossim = (cossim + 1) / 2  
    return normalized_cossim

@app.route("/")
def home():
    return render_template('base.html', title="Sample HTML")

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def spell_check(query, data_terms):
    corrected_query = []
    for term in query.split():
        min_distance = float('inf')
        closest_match = term
        for data_term in data_terms:
            distance = levenshtein_distance(term, data_term)
            if distance < min_distance:
                min_distance = distance
                closest_match = data_term
        corrected_query.append(closest_match)
    
    corrected_query_str = ' '.join(corrected_query)
    corrected = corrected_query_str != query
    return corrected_query_str, corrected

@app.route("/food_search")
def food_search():
    query = request.args.get("query")
    preprocessed_data = preprocess_data(data)
    term_frequency_matrix = create_term_frequency_matrix(preprocessed_data)
    
    all_terms = set()
    for city, matrix in term_frequency_matrix.items():
        all_terms.update(matrix.keys())

    corrected_query, corrected = spell_check(query, all_terms)
    print(corrected_query)
    query_vector = calculate_query_vector(corrected_query, term_frequency_matrix)
    similarities = {}
    for city, city_vector in term_frequency_matrix.items():
        cosine_sim = calculate_cosine_similarity(query_vector, city_vector)
        similarities[city] = cosine_sim

    top_10 = top_sim(similarities)
    top_10_json = [{"city": city, "similarity": similarity} for city, similarity in top_10]
    
    response = {"top_10": top_10_json, "original_query": query, "corrected_query": corrected_query}
    
    if corrected:
        response["corrected_query"] = corrected_query
    
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)