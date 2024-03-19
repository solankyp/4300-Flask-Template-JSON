import web_crawler
import wiki_parser
import json

def create_json(cities, topics):
    information = {}

    for city in cities:
        print("Scraping " + city + "...")
        if web_crawler.search_and_save(city):
            information[city] = {}
            for topic in topics:
                text = wiki_parser.scrape_wikitravel(city, topic)
                if text is not None:
                    information[city][topic] = text
                else:
                    print("Failed to crawl \"" + topic + "\" section for " + city)
        else:
            print("Failed to crawl WikiTravel page for " + city)

    file_path = "WikiTravel/dataset.json"

    with open(file_path, 'w') as json_file:
        json.dump(information, json_file)