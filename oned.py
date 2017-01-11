# 1D cellular automatons
from functools import partial
import random
# import itertools


def sliding_window(iterator, size=3):
    window = []
    for i, v in enumerate(iterator):
        window.append(v)
        if i >= size - 1:
            yield tuple(window)
            window.pop(0)


def get_rule(decimal_rule):
    options = ((1, 1, 1), (1, 1, 0), (1, 0, 1), (1, 0, 0),
               (0, 1, 1), (0, 1, 0), (0, 0, 1), (0, 0, 0))
    rule = tuple(int(r) for r in '{:08b}'.format(decimal_rule))
    return dict(zip(options, rule))


def print_rule(rule):
    rule = sorted(rule.items())
    print('|{}|'.format('|'.join(''.join(str(c) for c in opt)
                                 for opt, _ in rule)))
    print('|{}|'.format('|'.join('{: ^3}'.format(str(r))
                                 for _, r in rule)))


def print_configuration(config, width=79):
    start = 0
    if len(config) >= width:
        start = len(config) // 2 - width // 2
    print(
        '{: ^{width}}'.format(
            ''.join('#' if c else ' ' for c in config[start:start+width]),
            width=width
        )
    )


def get_next(current, rule_dict):
    current = (0, 0) + current + (0, 0)
    return tuple(rule_dict[w] for w in sliding_window(current))


def run_automaton(rule, start, steps=100, width=79):
    rule_dict = get_rule(rule)
    next_f = partial(get_next, rule_dict=rule_dict)
    n = start
    print_rule(rule_dict)
    for _ in range(steps):
        print_configuration(n, width=width)
        n = next_f(n)


def random_automaton(rule, density=.5, steps=100, width=79):
    n = tuple(1 if random.random() < density else 0 for _ in range(width))
    run_automaton(rule, n, steps=steps, width=width)


if __name__ == '__main__':
    random_automaton(184, 0.5, steps=1000, width=1000)
