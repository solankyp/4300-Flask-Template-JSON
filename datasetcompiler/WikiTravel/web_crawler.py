import requests
import utils
import os

def compose_url(city_name):
    url = "https://wikitravel.org/en/" + city_name
    return url

def crawl_page(url):
    # use header to avoid suspicious request
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    # Send a GET request to the provided URL
    response = requests.get(url, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        return response
    
    else:
        print("Crawler failed with error code: " + str(response.status_code))
        return None
    
def search_and_save(city_name):
    city_name = utils.replace_spaces(city_name)
    file_path = "WikiTravel/page_sources/" + city_name + ".html"

    if os.path.exists(file_path):
        return True

    # if page isn't already cached, scrape it
    response = crawl_page(compose_url(city_name))

    if response is not None:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
        return True
    else:
        print("Failed to fetch response")
        return False