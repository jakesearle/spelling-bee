import os
import re
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


def scrape_pokedex():
    pokedex_url = 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number'
    soup = get_soup(pokedex_url)
    generations = soup.select('table.roundy')
    pokemon = []
    for i, gen_table in enumerate(generations):
        gen_no = i + 1
        table_rows = gen_table.select('tr:has(td)')
        for row in table_rows:
            table_cells = row.select('td')
            dex_no = extract_integer(table_cells[0].get_text())
            # Skip alternate forms
            if dex_no is None:
                continue
            name = get_name(table_cells[2])
            if not is_valid_name(name):
                continue
            type1 = table_cells[3].get_text().strip().upper()
            type2 = None
            if len(table_cells) == 5:
                type2 = table_cells[4].get_text().strip().upper()
            pokemon.append(main.PokedexEntry(dex_no=dex_no, name=name, type1=type1, type2=type2, gen=gen_no))
    return pokemon


# From #0012 extract int(12)
def extract_integer(string):
    pattern = r'#(\d{1,})'
    match = re.search(pattern, string)
    if match:
        return int(match.group(1))
    else:
        return None


def get_name(name_element):
    name = name_element.select_one('a').get_text().strip().upper()
    name = name.replace('♀', '')
    name = name.replace('♂', '')
    return name


def is_valid_name(name):
    return all(['A' <= c <= 'Z' for c in name])


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
