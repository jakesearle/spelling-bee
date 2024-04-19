import ssl
from collections import Counter

import matplotlib.pyplot as plt
import nltk
import seaborn as sns
from nltk.corpus import brown

import scraper

BOX_HORIZONTAL = "─"
BOX_VERTICAL = "│"
BOX_DOWN_AND_RIGHT = "┌"
BOX_DOWN_AND_LEFT = "┐"
BOX_UP_AND_RIGHT = "└"
BOX_UP_AND_LEFT = "┘"
BOX_VERTICAL_AND_RIGHT = "├"
BOX_VERTICAL_AND_LEFT = "┤"
BOX_DOWN_AND_HORIZONTAL = "┬"
BOX_UP_AND_HORIZONTAL = "┴"
BOX_VERTICAL_AND_HORIZONTAL = "┼"

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('words', 'brown')
# wordlist_freq = nltk.FreqDist(words.words())
brown_freq = nltk.FreqDist(brown.words())


class Puzzle:
    def __init__(self, key_letter='X', other_letters=None):
        self.likely_pangrams = None
        self.likely_words = None
        self.all_words = None
        self.all_pangrams = None
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

    def grid_str(self):
        assert self.all_words is not None and self.all_pangrams is not None
        all_firsts = sorted(list(set([w[0] for w in self.all_words])))
        all_lengths = sorted(list(set([len(w) for w in self.all_words])))
        grid = [[0 for _ in all_lengths] for _ in all_firsts]
        first_sums = [0 for _ in all_firsts]
        len_sums = [0 for _ in all_lengths]
        for w in self.all_words:
            first_i = all_firsts.index(w[0])
            len_j = all_lengths.index(len(w))
            grid[first_i][len_j] += 1
            first_sums[first_i] += 1
            len_sums[len_j] += 1
        all_lengths = [str(l) for l in all_lengths]
        grid = [[str(i) if i != 0 else ' ' for i in j] for j in grid]
        first_sums = [str(i) for i in first_sums]
        len_sums = [str(i) for i in len_sums]
        cell_width = max([len(i) for i in first_sums + len_sums + [str(len(self.all_words))]]) + 2
        blank_inner_cell = ' ' * cell_width

        header_strs = [blank_inner_cell] + [i.center(cell_width) for i in all_lengths + ['Σ']]
        str_builder = " ".join(header_strs) + '\n'
        str_builder += blank_inner_cell + BOX_DOWN_AND_RIGHT + BOX_DOWN_AND_HORIZONTAL.join(
            [BOX_HORIZONTAL * cell_width for _ in range(len(all_lengths) + 1)]) + '\n'
        for i, first in enumerate(all_firsts):
            row_strs = [first] + grid[i] + [first_sums[i]]
            str_builder += BOX_VERTICAL.join([i.center(cell_width) for i in row_strs]) + '\n'
            str_builder += BOX_VERTICAL_AND_HORIZONTAL.join([BOX_HORIZONTAL * cell_width for _ in row_strs]) + '\n'
        footer_strs = ['Σ'] + len_sums + [str(len(self.all_words))]
        str_builder += BOX_VERTICAL.join([i.center(cell_width) for i in footer_strs]) + '\n'
        return str_builder

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
        header = [' ', *all_lengths, 'Σ']
        footer = ['Σ', *length_sums, sum(length_sums)]
        final_grid = [header] + surround(all_firsts, word_grid, first_sums) + [footer]
        return grid_str(final_grid)

    def n_words(self):
        assert self.all_words is not None
        return len(self.all_words)

    def median_word_frequency(self):
        return find_median([brown_freq[w.lower()] for w in self.all_words])

    def print_word_frequencies(self):
        data = [brown_freq[w.lower()] for w in self.all_words]
        print_histogram(data)


def surround(first_column, two_d_list, last_column):
    if len(first_column) != len(two_d_list) or len(last_column) != len(two_d_list):
        raise ValueError("Length of the first column list must be equal to the number of rows in the 2D list.")
    return [[cell1] + row + [cell2] for cell1, row, cell2 in zip(first_column, two_d_list, last_column)]


def get_puzzles(dictionary):
    pangrams = [w for w in dictionary if len(Counter(w)) == 7]
    puzzles = set()
    for p in pangrams:
        unique_letters = set(p)
        for let in unique_letters:
            puzzles.add(Puzzle.of(let, p))
    return puzzles


def find_median(lst):
    sorted_lst = sorted(lst)
    n = len(sorted_lst)
    if n % 2 == 1:
        return sorted_lst[n // 2]
    else:
        mid1 = sorted_lst[n // 2 - 1]
        mid2 = sorted_lst[n // 2]
        return (mid1 + mid2) / 2


def print_histogram(xs):
    sns.histplot(xs, kde=False, color='skyblue')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Histogram of Sample Data')
    plt.show()


def grid_str(values):
    string_values = [[str(cell) for cell in row] for row in values]
    rotated = zip(*string_values)
    column_widths = [max([max([len(w) for w in cell.split()] + [0]) for cell in col]) for col in rotated]
    row_heights = [max([max([len(cell.split())]) for cell in row] + [0]) for row in string_values]
    string_builder = ''
    for i, row in enumerate(string_values):
        # Fill extra row things
        sub_rows = [['' for _ in row] for _ in range(row_heights[i])]
        for i2, cell in enumerate(row):
            sub_cells = cell.split()
            for j2, s_cell in enumerate(sub_cells):
                sub_rows[j2][i2] = s_cell
        string_builder += '\n'.join([get_row_text(sub_row, column_widths) for sub_row in sub_rows]) + '\n'
        if i != len(string_values) - 1:
            string_builder += get_divider(column_widths) + '\n'
    return string_builder


def get_row_text(row, widths):
    return ' ' + f' {BOX_VERTICAL} '.join([cell.center(col_width) for cell, col_width in zip(row, widths)]) + ' '


def get_divider(widths):
    return BOX_HORIZONTAL + f'{BOX_HORIZONTAL}{BOX_VERTICAL_AND_HORIZONTAL}{BOX_HORIZONTAL}'.join(
        [BOX_HORIZONTAL * w for w in widths]) + BOX_HORIZONTAL


def get_dictionary():
    words = read_lines('collins-2019.txt')
    invalid = get_invalid_words()
    corpora_words = [w.upper() for w in words if len(w) >= 4]
    additional_words = get_valid_words()
    return list(set(w for w in corpora_words + additional_words if w not in invalid))


def read_lines(filename):
    with open(filename) as infile:
        return [line.strip() for line in infile.readlines()]


def get_invalid_words():
    return read_lines("invalid-words.txt")


def get_valid_words():
    return read_lines("valid-words.txt")


def main():
    # dictionary = get_dictionary()
    # test_puzzle = Puzzle.of('F', 'FAINTLY')
    # test_puzzle.solve(dictionary)
    words = scraper.scrape_words('https://www.sbsolver.com/s/2155')
    print(words)


if __name__ == '__main__':
    main()
