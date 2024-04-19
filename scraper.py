import os
from bs4 import BeautifulSoup

import requests

DIR = 'cache/'


def scrape_words(url):
    soup = get_soup(url)
    return [word_elem.get_text() for word_elem in soup.select('.bee-set td.bee-hover')]


def get_soup(url):
    filename = filename_from_url(url)
    filepath = DIR + filename
    if not os.path.exists(filepath):
        cache_url(url, filename)
    return load_soup_from_file(filepath)


def load_soup_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup


def cache_url(url, filename):
    response = requests.get(url)
    filepath = DIR + filename
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            file.write(response.content)
        print(f"HTML response saved as '{filepath}'.")
    else:
        print(f"Failed to fetch HTML response from '{url}'. Status code: {response.status_code}")


def create_cache():
    if not os.path.exists(DIR):
        os.makedirs(DIR)
    else:
        print(f"Directory '{DIR}' already exists.")


def filename_from_url(url):
    return url.replace('/', '_') + '.html'
