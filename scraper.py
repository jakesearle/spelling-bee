import os
from datetime import datetime

from bs4 import BeautifulSoup

import requests

import main

DIR = 'cache/'


def scrape_puzzle(url):
    soup = get_soup(url)
    words = [word_elem.get_text() for word_elem in soup.select('tr:not(.bee-disallowed) td.bee-hover')]
    center = soup.select_one('td span.bee-center').get_text()
    if not (words and center):
        raise Exception("Error in processing this puzzle")
    all_letters = set()
    for w in words:
        all_letters = all_letters.union(w)
        if len(all_letters) == 7:
            break
    date_str = soup.select_one('.crumb').get_text().split(' | ')[0]
    parsed_date = datetime.strptime(date_str, "%B %d, %Y")

    puzzle = main.Puzzle.of(center, all_letters)
    puzzle.all_words = words
    puzzle.date = parsed_date
    return puzzle


def scrape_retconned_words(url):
    soup = get_soup(url)
    words = [word_elem.get_text() for word_elem in soup.select('tr.bee-disallowed td.bee-hover')]
    return words


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
