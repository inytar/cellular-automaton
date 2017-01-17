import argparse
import functools
import operator
import random
import sys

import pygame as pg

import twod


class App(object):

    ALIVE = pg.Color('deeppink')
    DEAD = pg.Color('white')
    PAUSE = pg.Color('grey88')

    def __init__(self, rule='B3/S23M', density=0, color=True):
        """A 2D cellular automaton game.

        rule: str: A valid cellular automaton rule, in the format
        'B{}/S{}[MV]', where M and V are Moore neighbours (every cell has
        8 neighbours) and Von Nuemann neighbours (every cell has 4
        neighbours). B{} is the birth rate, and S{} the survival rate. The
        game of live is 'B3/S23M'.
        density: float: The density of alive cell on start, a number between
        0 (no alive cells) and 100 (all cell alive) can be used.
        """
        self._running = False
        self.color = color
        if not self.color:
            self.ALIVE = pg.Color('black')
        self._display_surf = None
        self.density = density
        self.size = self.width, self.height = 640, 640
        self.rule = twod.get_rule(rule)
        self.cell_size = 8
        self.framerate = 5
        # print(tuple(v // self.cell_size for v in self.size))
        self.state = twod.create_array(
            map(operator.methodcaller('__floordiv__', self.cell_size),
                self.size),
            self.density)

    def on_init(self):
        pg.init()
        self._display_surf = pg.display.set_mode(
            self.size,
            pg.HWSURFACE | pg.DOUBLEBUF
        )
        pg.display.set_caption('Cellular Automaton')
        self._clock = pg.time.Clock()
        self._running = True
        self.play = False
        self.create = None
        self.one_step = False
        self.render_state()
        pg.display.flip()

    def on_event(self, event):
        if event.type == pg.QUIT:
            self._running = False
            return
        if not self.play and event.type == pg.MOUSEBUTTONDOWN:
            cell_pos = self.get_mouse_cell()
            self.create = not self.state[cell_pos[1]][cell_pos[0]]
        if event.type == pg.MOUSEBUTTONUP:
            self.create = None
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.create = None
                self.play = not self.play
            if event.key == pg.K_RIGHT:
                self.create = None
                self.play = True
                self.one_step = True

    def get_mouse_cell(self):
        return tuple(p // self.cell_size for p in pg.mouse.get_pos())

    def on_loop(self):
        if self.play:
            self._clock.tick(self.framerate)
            self.state = twod.next_state(self.state, self.rule)
            if self.one_step:
                self.play = False
                self.one_step = False
            if self.color:
                self.ALIVE.hsla = ((self.ALIVE.hsla[0] + 1) % 360,) + \
                    self.ALIVE.hsla[1:]
            return
        self._clock.tick(self.framerate * 2)
        if self.create is not None:
            cell_pos = self.get_mouse_cell()
            if self.create:
                self.state = twod.bear_cell(cell_pos, self.state)
            else:
                self.state = twod.kill_cell(cell_pos, self.state)

    def render_state(self):
        background = self.DEAD
        if not self.play:
            background = self.PAUSE
        self._display_surf.fill(background)
        for y in range(self.height // self.cell_size):
            for x in range(self.width // self.cell_size):
                cell = self.state[y][x]
                if cell:
                    color = self.ALIVE
                    if self.color:
                        color = pg.Color(*color)
                        color.hsla = ((color.hsla[0] + cell.time_spam)
                                      % 360,) + \
                            color.hsla[1:]
                    x_loc = x * self.cell_size
                    y_loc = y * self.cell_size
                    self._display_surf.fill(
                        color,
                        rect=(x_loc, y_loc, self.cell_size, self.cell_size)
                    )

    def on_render(self):
        self.render_state()
        pg.display.flip()

    def on_cleanup(self):
        pg.quit()

    def on_execute(self):
        self.on_init()
        while self._running:
            for event in pg.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
            # print(self._clock.get_fps())
        self.on_cleanup()


def parse_args():
    parser = argparse.ArgumentParser(
        description='A 2D cellular automaton game'
    )
    default_rule = 'B3/S23M'
    default_density = 0
    parser.add_argument('rule', nargs='?',
                        help='the rule of the game')
    parser.add_argument('density', nargs='?', type=float,
                        help='the starting density of the game')
    parser.add_argument('--no-color', '-nc', help='run in black and white',
                        action='store_false', dest='color')
    arguments = parser.parse_args()
    if arguments.density is None and arguments.rule:
        try:
            arguments.density = float(arguments.rule)
        except ValueError:
            pass
        else:
            arguments.rule = None
    if arguments.density is None:
        arguments.density = default_density
    if arguments.rule is None:
        arguments.rule = default_rule
    elif not twod.rule_re.match(arguments.rule):
        parser.error('Invalid rule!')
    return vars(arguments)


def main():
    arguments = parse_args()
    app = App(**arguments)
    app.on_execute()


if __name__ == "__main__":
    sys.exit(main())
