import ssl
from collections import Counter
import random
from datetime import date

import cache
import matplotlib.pyplot as plt
import nltk
import seaborn as sns
from nltk.corpus import brown
from tqdm import tqdm

import scraper
import util
from util import grid_str, surround, find_median

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('brown')
brown_freq = nltk.FreqDist(brown.words())


class PokedexEntry:
    def __init__(self, dex_no=0, name='', type1='', type2='', gen=0):
        self.dex_no = dex_no
        self.name = name
        self.type1 = type1
        self.type2 = type2
        self.gen = gen
        if self.type2 is None:
            self.type2 = "NONE"

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str((self.gen, self.dex_no, self.name, self.type1, self.type2))


class Puzzle:
    def __init__(self, key_letter='X', other_letters=None):
        self.all_words = None
        self.all_pangrams = None
        self.date = date.today()
        self.key_letter = key_letter

        if other_letters is None:
            self.other_letters = []
        else:
            self.other_letters = other_letters

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        let_str = ' '.join(self.other_letters)
        return f"({self.key_letter}) {let_str}"

    def __eq__(self, other):
        if isinstance(other, Puzzle):
            return self.__str__() == other.__str__()
        return False

    def __hash__(self):
        return hash(self.__str__())

    @staticmethod
    def of(key, word):
        other_letters = sorted(list(set([c for c in word if c != key])))
        return Puzzle(key_letter=key, other_letters=other_letters)

    def all_letters(self):
        return self.other_letters + [self.key_letter]

    def is_valid(self):
        all_letters = self.all_letters()
        if 'S' in all_letters:
            return False
        if 'E' in all_letters and 'R' in all_letters:
            return False
        return True

    def has(self, letter):
        return letter in self.all_letters()

    def contains_word(self, word):
        return self.key_letter in word and all([self.has(let) for let in word])

    def is_pangram(self, word):
        return set(word) == set(self.all_letters())

    def is_perfect_pangram(self, word):
        return self.is_pangram(word) and len(word) == 7

    def solve(self, dictionary):
        self.all_words = [w for w in dictionary if self.contains_word(w)]
        self.all_pangrams = [w for w in self.all_words if self.is_pangram(w)]

    def solution_grid(self):
        all_firsts = sorted(list(set([w[0] for w in self.all_words])))
        all_lengths = sorted(list(set([len(w) for w in self.all_words])))
        first_sums = [sum([1 for w in self.all_words if w[0] == f]) for f in all_firsts]
        length_sums = [sum([1 for w in self.all_words if len(w) == l]) for l in all_lengths]
        grouped_words = {}
        for w in sorted(self.all_words):
            if (w[0], len(w)) in grouped_words:
                grouped_words[(w[0], len(w))].append(w)
            else:
                grouped_words[(w[0], len(w))] = [w]
        word_grid = [['\n'.join(grouped_words.get((f, l), '')) for l in all_lengths] for f in all_firsts]
        header = ['', *all_lengths, 'Σ']
        footer = ['Σ', *length_sums, sum(length_sums)]
        final_grid = [header] + surround(all_firsts, word_grid, first_sums) + [footer]
        grid_string = grid_str(final_grid)
        title = f'{self.date_str()} | {self.__str__()}'
        return f'{title}\n{grid_string}'

    def solution_grid_markdown(self):
        all_firsts = sorted(list(set([w[0] for w in self.all_words])))
        all_lengths = sorted(list(set([len(w) for w in self.all_words])))
        first_sums = [sum([1 for w in self.all_words if w[0] == f]) for f in all_firsts]
        length_sums = [sum([1 for w in self.all_words if len(w) == l]) for l in all_lengths]
        grouped_words = {}
        for w in sorted(self.all_words):
            if (w[0], len(w)) in grouped_words:
                grouped_words[(w[0], len(w))].append(w)
            else:
                grouped_words[(w[0], len(w))] = [w]
        word_grid = [['<br>'.join(grouped_words.get((f, l), '')) for l in all_lengths] for f in all_firsts]
        # Add spoilertext
        word_grid = [[f'>!{cell}!<' if cell else cell for cell in row] for row in word_grid]
        header = ['', *all_lengths, 'Σ']
        footer = ['Σ', *length_sums, sum(length_sums)]
        final_grid = [header] + surround(all_firsts, word_grid, first_sums) + [footer]
        grid_string = util.markdown_table(final_grid)
        title = f'{self.date_str()} | {self.__str__()}'
        return f'{title}\n\n{grid_string}'

    def n_words(self):
        assert self.all_words is not None
        return len(self.all_words)

    def median_word_frequency(self):
        return find_median([brown_freq[w.lower()] for w in self.all_words])

    def median_word_length(self):
        return find_median([len(w) for w in self.all_words])

    def print_word_frequencies(self):
        data = [brown_freq[w.lower()] for w in self.all_words]
        print_histogram(data)

    def calc_pangrams(self):
        assert self.all_words is not None
        letter_set = set(self.all_letters())
        self.all_pangrams = [w for w in self.all_words if set(w) == letter_set]

    def date_str(self):
        if self.date is None:
            return ''
        return self.date.strftime("%B %d, %Y")

    def pokedex_markdown(self, pokedex):
        valid = [p for p in pokedex if self.contains_word(p.name)]
        self.all_words = [p.name for p in valid]
        return (f'{self.pokedex_normal_hint_grid(valid)}\n\n'
                f'**Type Grid**\n\n'
                f'{self.pokedex_type_grid(valid)}\n\n'
                f'**Generation List**\n\n'
                f'{self.pokedex_generation_hints(valid)}\n\n'
                f'**Solution**\n\n'
                f'{self.solution_grid_markdown()}')

    def pokedex_normal_hint_grid(self, answers):
        all_names = [p.name for p in answers]
        pokegrams = [p for p in answers if self.is_pangram(p.name)]
        perfect_pokegrams = [p for p in answers if self.is_perfect_pangram(p.name)]

        all_firsts = sorted(list(set([n[0] for n in all_names])))
        all_lengths = sorted(list(set([len(n) for n in all_names])))
        first_sums = [sum([1 for w in all_names if w[0] == f]) for f in all_firsts]
        length_sums = [sum([1 for w in all_names if len(w) == l]) for l in all_lengths]
        word_grid = [[sum([1 for n in all_names if n[0] == f and len(n) == l]) for l in all_lengths] for f in
                     all_firsts]
        # Remove zeros
        word_grid = [[c if c else '' for c in row] for row in word_grid]
        header = ['', *all_lengths, 'Σ']
        footer = ['Σ', *length_sums, sum(length_sums)]
        final_grid = [header] + surround(all_firsts, word_grid, first_sums) + [footer]

        str_builder = f'This puzzle has {len(answers)} Pokémon'
        if pokegrams:
            str_builder += f', with {len(pokegrams)} Pokégrams'
        if perfect_pokegrams:
            str_builder += f', and {len(perfect_pokegrams)} perfect Pokégrams'
        if not pokegrams and not perfect_pokegrams:
            str_builder += f', with no Pokégrams'
        str_builder += '\n\n'
        str_builder += util.markdown_table(final_grid)
        return str_builder

    def pokedex_type_grid(self, poke_answers):
        all_primary_types = sorted(list(set([p.type1 for p in poke_answers])))
        all_secondary_types = sorted(list(set([p.type2 for p in poke_answers])))
        # Move "NONE" to the front
        if "NONE" in all_secondary_types:
            all_secondary_types.remove("NONE")
            all_secondary_types = ["NONE"] + all_secondary_types
        primary_sums = [sum([1 for p in poke_answers if p.type1 == t]) for t in all_primary_types]
        secondary_sums = [sum([1 for p in poke_answers if p.type2 == t]) for t in all_secondary_types]
        grid = [[sum([1 for p in poke_answers if p.type1 == t1 and p.type2 == t2]) for t2 in all_secondary_types] for t1
                in all_primary_types]

        header = ['↓Secondary/Primary→', *all_secondary_types, 'Σ']
        footer = ['Σ', *secondary_sums, sum(primary_sums)]
        return util.markdown_table([header] + surround(all_primary_types, grid, primary_sums) + [footer])

    def pokedex_generation_hints(self, poke_answers):
        gens = sorted(list(set([p.gen for p in poke_answers])))
        gen_strs = [f'Gen. {g}' for g in gens]
        gen_sums = [sum([1 for p in poke_answers if p.gen == g]) for g in gens]
        grid = [[label, total] for label, total in zip(gen_strs, gen_sums)]
        return util.markdown_table(grid)


def is_blankspace(string):
    return all([c.isspace() for c in string])


def get_puzzles(dictionary):
    pangrams = [w for w in dictionary if len(Counter(w)) == 7]
    puzzles = set()
    for p in pangrams:
        unique_letters = set(p)
        for let in unique_letters:
            puzzles.add(Puzzle.of(let, p))
    return puzzles


def print_histogram(xs, title='Title'):
    sns.histplot(xs, kde=False, color='skyblue')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title(title)
    plt.show()


def get_my_solves(dictionary, real_puzzles):
    ret = []
    for p in tqdm(real_puzzles):
        my_p = Puzzle.of(p.key_letter, p.other_letters)
        my_p.solve(dictionary)
        ret.append(my_p)
    return ret


def longest_non_pangram():
    words = cache.load_dictionary('verified-words')
    puzzles = cache.load_all_puzzles()
    # Find longest
    target = max([len(w) for w in words if len(set(w)) < 7])
    # Find all longest
    longest = [w for w in words if len(set(w)) < 7 and len(w) == target]
    # Print dates
    dates = [p.date_str() for p in puzzles if any([w in p.all_words for w in longest])]
    print(dates)


def retconned_pangrams():
    retcons = cache.load_retconned_words()
    rp = [w for w in retcons if len(set(w)) == 7]
    print(f'There have been {len(rp)} retconned pangrams')
    print(f'{"\n".join(rp)}')


def absent_ngrams(ngram):
    puzzles = cache.load_all_puzzles()
    reduced_ngram = list(set(ngram))
    puzzles_w_ngram = [p for p in puzzles if all([c in p.all_letters() for c in reduced_ngram])]
    print(f"Puzzles that contain {ngram}: {len(puzzles_w_ngram)}")
    puzzles_without_ngram_in_word = [p for p in puzzles_w_ngram if not any([ngram in w for w in p.all_words])]
    print(f"Puzzles that contain {ngram} with no words that contain {ngram}: {len(puzzles_without_ngram_in_word)}")
    for p in puzzles_without_ngram_in_word:
        print(p.solution_grid())


def unverified_description():
    unverified = cache.load_unverified_words()
    # Contain S
    have_s = [w for w in unverified if 'S' in w]
    print(f'{(len(have_s) / len(unverified) * 100.0):.2f}% of unverified words contain \'S\' '
          f'({len(have_s):,}/{len(unverified):,})')
    # Contain ER
    have_er = [w for w in unverified if 'E' in w and 'R' in w]
    print(f'{(len(have_er) / len(unverified) * 100.0):.2f}% of unverified words contain \'E\' and \'R\' '
          f'({len(have_er):,}/{len(unverified):,})')
    # Have +7 unique letters
    have_plus7_letters = [w for w in unverified if len(set(w)) > 7]
    print(f'{(len(have_plus7_letters) / len(unverified) * 100.0):.2f}% of unverified words have more than 7 unique '
          f'letters ({len(have_plus7_letters):,}/{len(unverified):,})')

    # Other
    other = unverified - set(have_s) - set(have_er) - set(have_plus7_letters)
    print(f'{(len(other) / len(unverified) * 100.0):.2f}% of don\'t fit these criteria '
          f'({len(other):,}/{len(unverified):,})')
    # Median scrabble score of other
    median = util.find_median([util.scrabble_score(w) for w in other])
    print(f'  These words have an median scrabble score of: {median}')
    print(f'  Here are some examples of them:')
    for w in random.sample(sorted(other), 10):
        print(f'  {w} ({util.scrabble_score(w)})')
    # Have 7 unique letters
    have_7_letters = [w for w in other if len(set(w)) == 7]
    print(f'{(len(have_7_letters) / len(other) * 100.0):.2f}% of "other" words have exactly 7 unique letters '
          f'({len(have_7_letters):,}/{len(other):,})')


def solve_today(key, other_letters):
    puzz = Puzzle.of(key, other_letters)
    likely_words = cache.load_likely_words()
    verified_words = cache.load_dictionary('verified-words')
    solving_words = likely_words.union(verified_words)
    puzz.solve(solving_words)
    print(puzz.solution_grid())


def solve_with_pokedex(key, other_letters):
    puzz = Puzzle.of(key, other_letters)
    pokedex = cache.load_pokedex()
    with open('temp.md', 'w') as outfile:
        outfile.write(puzz.pokedex_markdown(pokedex))


def main():
    solve_with_pokedex("U", "NLMBTA")


if __name__ == '__main__':
    main()
