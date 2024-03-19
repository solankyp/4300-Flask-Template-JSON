import utils
from bs4 import BeautifulSoup



def scrape_wikitravel(city_name, heading_name):
    
    city_name = utils.replace_spaces(city_name)
    file_path = "WikiTravel/page_sources/" + city_name + ".html"

    with open(file_path, 'r', encoding='utf-8') as file:
        html = file.read()
    
    soup = BeautifulSoup(html, 'lxml')

    # Find the section with the "Do" heading
    span_do = soup.find('span', id=heading_name)

    # Navigate to the next sibling, which is the <p> tag containing the text
    if span_do:
        doc = ""
        # Optionally, navigate to the enclosing <h2> if you need it for some reason
        # h2_do = span_do.find_parent('h2')
        
        # Start processing the siblings of the <h2> tag that contains the <span>
        for sibling in span_do.find_parent('h2').find_next_siblings():
            if sibling.name == 'h2':
                break  # Stop if we reach another <h2> element
            doc = doc + sibling.get_text(strip=True)
        return doc
    else:
        return None