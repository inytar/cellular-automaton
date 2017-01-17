# Two dimensional cellular automatons
from functools import partial
import random
import re


rule_re = re.compile(r'^B\d*/S\d*[MV]?$')


def alive_neighbours(position, array, diagonals='M'):
    # diagonals=True means Moore neighbours, else Von Neumann neighbours.
    y_len = len(array)
    # We assume that the array is always rectangular.
    x_len = len(array[0])
    if diagonals == 'V':
        def filter_(x, y):
            return x == 0 or y == 0 and x != y
    else:
        def filter_(x, y):
            return not x == y == 0
    neighbours = (array[position[1] + y if position[1] + y < y_len else 0]
                  [position[0] + x if position[0] + x < x_len else 0]
                  for y in range(-1, 2)
                  for x in range(-1, 2) if filter_(x, y))
    return sum(neighbours)


def get_rule(str_rule):
    # A rule is in the format B{}/S{}[M|V] where B{} gives the amount of
    # neighbours on which a dead cell will be born, S{} gives the amount of
    # neighbours on which a live cell will survive and [M|V] indicates if
    # Moore neighbours are used or Von Neumann. If no M or V is given
    # Moore neighbours are assumed.
    diagonals = str_rule[-1].upper()
    if diagonals not in ('M', 'V'):
        diagonals = 'M'
    if not str_rule[-1].isdigit():
        str_rule = str_rule[:-1]
    return tuple(tuple(int(i) for i in s[1:]) for s in str_rule.split('/')) + \
        tuple(diagonals)


def print_rule(rule):
    print('B{0[0]}/S{0[1]}{1}'.
          format(tuple(''.join(str(d) for d in t) for t in rule[:-1]),
                 rule[2]))


def next_state(current, rule):
    return tuple(
        tuple(
            (current[y][x].bear() if
             alive_neighbours((x, y), current, rule[2]) in
             rule[current[y][x]] else current[y][x].kill()) for
            x in range(len(current[y]))
        ) for y in range(len(current))
    )


def create_array(size, density=50):
    size = tuple(size)
    return tuple(
        tuple(Alive() if random.random() * 100 < density else Dead()
              for _x in range(size[1]))
        for _y in range(size[0])
    )


def invert_cell(cell_pos, array):
    cell_pos = tuple(cell_pos)
    return tuple(
        tuple(
            array[y][x] if (x, y) != cell_pos else ~array[x][y]
            for x in range(len(array[y]))
        ) for y in range(len(array))
    )


def invert(array):
    return tuple(
        tuple(
            ~v for v in row
        ) for row in array
    )


def bear_cell(cell_pos, array):
    return tuple(
        tuple(
            array[y][x] if (x, y) != cell_pos else array[y][x].bear()
            for x in range(len(array[y]))
        ) for y in range(len(array))
    )


def kill_cell(cell_pos, array):
    return tuple(
        tuple(
            array[y][x] if (x, y) != cell_pos else array[y][x].kill()
            for x in range(len(array[y]))
        ) for y in range(len(array))
    )


def run_automaton(rule, start, steps=10):
    rule = get_rule(rule)
    next_f = partial(next_state, rule=rule)
    n = start
    print_rule(rule)
    for _ in range(steps):
        print_state(n)
        n = next_f(n)


def print_state(array):
    print('_' * len(array[0]) + '__')
    print('|{}|'.format('|\n|'.join(
        ''.join('#' if c else ' ' for c in r) for r in array
    )))
    print('‾' * len(array[-1]) + '‾‾')


def random_automaton(rule, size, density=50, steps=10):
    start = create_array(size, density)
    run_automaton(rule, start, steps)


class Alive(int):

    def __new__(cls):
        return super().__new__(cls, 1)

    def __init__(self, time_spam=0):
        self.time_spam = time_spam

    def __invert__(self):
        return Dead()

    def bear(self):
        self.time_spam += 1
        return self

    def kill(self):
        return Dead()


class Dead(int):

    def __new__(cls):
        return super().__new__(cls, 0)

    def __init__(self, time_spam=0):
        self.time_spam = time_spam

    def __invert__(self):
        return Alive()

    def bear(self):
        return Alive()

    def kill(self):
        self.time_spam += 1
        return self


if __name__ == '__main__':
    random_automaton('B3/S23M', (5, 205), density=10, steps=10)
