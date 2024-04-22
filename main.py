import ssl
from collections import Counter
import random

import cache
import matplotlib.pyplot as plt
import nltk
import seaborn as sns
from nltk.corpus import brown
from tqdm import tqdm

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


class Puzzle:
    def __init__(self, key_letter='X', other_letters=None):
        self.all_words = None
        self.all_pangrams = None
        self.date = None
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

    def solve(self, dictionary):
        self.all_words = [w for w in dictionary if self.contains_word(w)]
        self.all_pangrams = [w for w in self.all_words if self.is_pangram(w)]

    def solution_str(self):
        str_builder = ''
        sorted_words = sorted(self.all_words, key=lambda x: (x[0], len(x)))
        for i, word in enumerate(sorted_words):
            if i > 0 and (len(sorted_words[i - 1]) != len(word) or sorted_words[i - 1][0] != word[0]):
                str_builder += '-' * max(len(sorted_words[i - 1]), len(word)) + '\n'
            str_builder += word + '\n'
        return str_builder

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


def differences(solves1, solves2):
    return [len(set(s1.all_words).symmetric_difference(set(s2.all_words))) for s1, s2 in zip(solves1, solves2)]


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


def main():
    like = cache.load_likely_words()


if __name__ == '__main__':
    main()
