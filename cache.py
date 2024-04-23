import os

import jsonpickle
from tqdm import tqdm

import scraper
from main import Puzzle

DIR = 'cache/'
# Just manually fix this number from this link: https://www.sbsolver.com/archive
LATEST = 2176


# Not a python dictionary, but a dictionary of words
def save_dictionary(iterable, dictionary_name):
    dictionary_name = add_txt_extension(dictionary_name)
    words = sorted(list({w.upper() for w in iterable}))
    with open(dictionary_name, "w") as outfile:
        outfile.write('\n'.join(words))


def load_dictionary(dictionary_name):
    dictionary_name = add_txt_extension(dictionary_name)
    with open(dictionary_name, 'r') as infile:
        return {w.strip() for w in infile.readlines()}


def load_all_puzzles():
    filepath = DIR + 'old-puzzles.ndjson'
    if not os.path.exists(filepath):
        save_all_puzzles(filepath)
    return load_pickle_ndjson(filepath)


def save_all_puzzles(filepath):
    prev_puzzles = [scraper.scrape_puzzle(f'https://www.sbsolver.com/s/{i}') for i in
                    tqdm(reversed(range(1, LATEST + 1)))]
    for p in prev_puzzles:
        p.calc_pangrams()
    save_ndjson(prev_puzzles, filepath)


def add_txt_extension(string):
    if not string.endswith('.txt'):
        string += '.txt'
    return string


def save_ndjson(list_of_puzzles, filepath):
    scraper.create_cache()
    with open(filepath, 'w') as outfile:
        out_str = '\n'.join(jsonpickle.encode(p) for p in list_of_puzzles)
        outfile.write(out_str)


def load_pickle_ndjson(filepath):
    with open(filepath, 'r') as infile:
        return [jsonpickle.decode(line) for line in infile.readlines()]


def load_scrabble_dictionary():
    word_list = read_lines('collins-2019.txt')
    return set([w.upper() for w in word_list if len(w) >= 4])


def read_lines(filename):
    with open(filename) as infile:
        return [line.strip() for line in infile.readlines()]


def load_retconned_words():
    filepath = 'retconned-words.txt'
    if not os.path.exists(filepath):
        retconned_word_lists = [scraper.scrape_retconned_words(f'https://www.sbsolver.com/s/{i}') for i in
                                tqdm(reversed(range(1, LATEST + 1)))]
        retconned_words = [w for l in retconned_word_lists for w in l]
        save_dictionary(retconned_words, filepath)
    return load_dictionary(filepath)


def load_unverified_words():
    filepath = 'unverified-words.txt'
    if not os.path.exists(filepath):
        save_unverified_words(filepath)
    return load_dictionary(filepath)


def save_unverified_words(filename):
    scrabble_dictionary = load_scrabble_dictionary() - load_retconned_words()
    official_puzzles = load_all_puzzles()
    unverified_words = scrabble_dictionary.copy()
    # Re-solve all puzzles
    for official_solve in tqdm(official_puzzles):
        my_solve = Puzzle.of(official_solve.key_letter, official_solve.other_letters)
        my_solve.solve(scrabble_dictionary)
        illegal_words = set(my_solve.all_words) - set(official_solve.all_words)
        # Refine scrabble dictionary
        scrabble_dictionary -= illegal_words
        # Eliminate verified and illegal words
        unverified_words -= set(my_solve.all_words)
    print(f'Found {len(unverified_words)} unverified words')
    save_dictionary(unverified_words, filename)


def load_likely_words():
    filepath = 'likely-words.txt'
    if not os.path.exists(filepath):
        save_likely_words(filepath)
    return load_dictionary(filepath)


def save_likely_words(filename):
    unverified = load_unverified_words()
    # Contain S
    have_s = [w for w in unverified if 'S' in w]
    # Contain ER
    have_er = [w for w in unverified if 'E' in w and 'R' in w]
    # Have +7 unique letters
    have_plus7_letters = [w for w in unverified if len(set(w)) > 7]
    # Other
    likely_words = unverified - set(have_s) - set(have_er) - set(have_plus7_letters)
    save_dictionary(likely_words, filename)


def load_pokedex():
    filepath = DIR + 'pokedex.ndjson'
    if not os.path.exists(filepath):
        save_pokedex(filepath)
    return load_pickle_ndjson(filepath)


def save_pokedex(filepath):
    pokedex = scraper.scrape_pokedex()
    save_ndjson(pokedex, filepath)
