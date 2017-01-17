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
            (1 if alive_neighbours((x, y), current, rule[2]) in
             rule[current[y][x]] else 0) for
            x in range(len(current[y]))
        ) for y in range(len(current))
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


def random_automaton(rule, size, density=.5, steps=10):
    start = tuple(
        tuple(1 if random.random() < density else 0
              for _y in range(size[1]))
        for _x in range(size[0])
    )
    run_automaton(rule, start, steps)


if __name__ == '__main__':
    random_automaton('B2/S2M', (5, 205), density=.05, steps=30)
