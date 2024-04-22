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

SCRABBLE_SCORES = {
    "A": 1, "B": 3, "C": 3, "D": 2, "E": 1, "F": 4, "G": 2, "H": 4, "I": 1, "J": 8, "K": 5, "L": 1, "M": 3, "N": 1,
    "O": 1, "P": 3, "Q": 10, "R": 1, "S": 1, "T": 1, "U": 1, "V": 4, "W": 4, "X": 8, "Y": 4, "Z": 10
}


def surround(first_column, two_d_list, last_column):
    if len(first_column) != len(two_d_list) or len(last_column) != len(two_d_list):
        raise ValueError("Length of the first column list must be equal to the number of rows in the 2D list.")
    return [[cell1] + row + [cell2] for cell1, row, cell2 in zip(first_column, two_d_list, last_column)]


def find_median(lst):
    sorted_lst = sorted(lst)
    n = len(sorted_lst)
    if n % 2 == 1:
        return sorted_lst[n // 2]
    else:
        mid1 = sorted_lst[n // 2 - 1]
        mid2 = sorted_lst[n // 2]
        return (mid1 + mid2) / 2


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


def print_adjacent(multiline_string1, multiline_string2):
    lines1 = multiline_string1.split('\n')
    lines2 = multiline_string2.split('\n')
    # Fill the lists
    max_height = max(len(lines1), len(lines2))
    lines1 += [''] * (max_height - len(lines1))
    lines2 += [''] * (max_height - len(lines2))

    max_length = max([len(line) for line in lines1])
    for l, r in zip(lines1, lines2):
        print(f'{l.ljust(max_length)} {r}')


def scrabble_score(word):
    return sum([SCRABBLE_SCORES[letter] for letter in word])
