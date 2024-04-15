import json
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import re
from collections import defaultdict
import math
import pickle
import numpy as np

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

import pandas as pd

csv_file_path = os.path.join(current_directory, 'programs.csv')
cities_df = pd.read_csv(csv_file_path)
cities_series = cities_df['City'].astype(str).str.strip()
allowed_cities_set = set(cities_series.unique())

program_desc = cities_df['Description'].astype(str).str.strip()


def load_school_data():
    schools_with_descriptions = cities_df.groupby('City').apply(lambda x: x[['School', 'Description']].to_dict('records')).to_dict()
    return schools_with_descriptions


def preprocess_data(data):
    preprocessed_data = defaultdict(dict)
    for city, categories in data.items():
        for _, details in categories.items():
            food_info = details.get('Eat')
            activities = details.get('Do')
            buy = details.get('Buy')
            see = details.get('See')
            if food_info is not None:
                preprocessed_data[city]['Eat'] = food_info 
            if activities is not None:
                preprocessed_data[city]['Do'] = activities
            if buy is not None:
                preprocessed_data[city]['Buy'] = buy
            if see is not None:
                preprocessed_data[city]['See'] = see
    return preprocessed_data

def create_term_frequency_matrix(data, sections_pressed):
    term_frequency_matrix = defaultdict(dict)
    if not any(sections_pressed):
        sections_pressed = [True, True, True, True]
    for city, city_data in data.items():
        for index, (_, pressed) in enumerate(city_data.items()):
            if sections_pressed[index]:
                info = pressed
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

def calculate_svd_similarities(query):
    # retrieve SVD matrices from pickle
    with open("static/svd_vars.pkl", 'rb') as f:
        svd_vars = pickle.load(f)
    docs_compressed_normed = svd_vars['docs_compressed_normed']
    words_compressed_normed = svd_vars['words_compressed_normed']
    cities = svd_vars['cities']
    vocab = svd_vars['vocab']

    # get svd similarities
    words = query.split(" ")
    sims_sum = np.zeros(len(docs_compressed_normed))
    for word in words:
        if word not in vocab: continue
        sims = docs_compressed_normed.dot(words_compressed_normed[vocab[word],:])
        sims_sum = sims + sims

    # min-max scale the similarities to be between 0 and 1:
    min_sim = min(sims_sum)
    max_sim = max(sims_sum)
    sims_sum = [(sim - min_sim) / (max_sim - min_sim) for sim in sims_sum]

    city_sim_dict = {}
    for i, sim in enumerate(sims_sum):
        city_sim_dict[cities[i]] = sim

    return city_sim_dict

def merge_similarities(cosine_dict, svd_dict, cosine_weight, svd_weight):
    """
    merge cosine and svd similarities for a given query according to the weights
    """
    cosine_keys = set(cosine_dict.keys())
    svd_keys = set(svd_dict.keys())
    merged_keys = cosine_keys.intersection(svd_keys)

    similarities = {}
    for key in merged_keys:
        similarities[key] = (cosine_weight * cosine_dict[key]) + (svd_weight * svd_dict[key])
        # print("KEY = " + str(key))
        # print("COSINE = " + str(cosine_dict[key]))
        # print("SVD = " + str(svd_dict[key]))
    return similarities

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
    sections = request.args.getlist("section")

    sections_pressed = [False, False, False, False]
    for section in sections:
        if section == 'Eat':
            sections_pressed[0] = True
        elif section == 'Do':
            sections_pressed[1] = True
        elif section == 'Buy':
            sections_pressed[2] = True
        elif section == 'See':
            sections_pressed[3] = True

    if not any(sections_pressed):
        sections_pressed = [True, True, True, True]
    print(sections_pressed)
    preprocessed_data = preprocess_data(data)
    term_frequency_matrix = create_term_frequency_matrix(preprocessed_data, sections_pressed)

    all_terms = set()
    for city, matrix in term_frequency_matrix.items():
        all_terms.update(matrix.keys())

    corrected_query, corrected = spell_check(query, all_terms)
    query_vector = calculate_query_vector(corrected_query, term_frequency_matrix)

    # cosine similarities
    cosine_similarities = {}
    for city, city_vector in term_frequency_matrix.items():
        if city in allowed_cities_set:
            cosine_sim = calculate_cosine_similarity(query_vector, city_vector)
            cosine_similarities[city] = cosine_sim


    # svd similarities
    svd_similarities = calculate_svd_similarities(corrected_query)

    # merge svd and similarity dicts
    similarities = merge_similarities(cosine_dict=cosine_similarities,
                                      svd_dict=svd_similarities,
                                      cosine_weight=0.8,
                                      svd_weight=0.2)
    schools_with_descriptions = load_school_data()
    top_10 = top_sim(similarities)

    top_10_with_schools_and_descriptions = []
    for city, _ in top_10:
        school_info = schools_with_descriptions.get(city, [])
        top_10_with_schools_and_descriptions.append({
            'city': city,
            'cos_similarity': cosine_similarities.get(city, 0),
            'svd_similarity': svd_similarities.get(city, 0),
            'school_info': school_info  # This now includes the descriptions
        })
    print(school_info )
    response = {
            "top_10": top_10_with_schools_and_descriptions,
            "original_query": query,
            "corrected_query": corrected_query
        }
    
    if corrected:
        response["corrected_query"] = corrected_query
    print(json.dumps(top_10_with_schools_and_descriptions, indent=4))

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)