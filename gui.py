import argparse
import random
import sys

import pygame as pg

import twod


class App(object):

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREY = (218, 218, 218)

    def __init__(self, rule='B3/S23M', density=0):
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
        self._display_surf = None
        self.density = density
        self.size = self.width, self.height = 640, 640
        self.rule = twod.get_rule(rule)
        self.cell_size = 8
        self.framerate = 5
        # print(tuple(v // self.cell_size for v in self.size))
        self.state = tuple(
            tuple(
                1 if random.random() * 100 < self.density else 0
                for _x in range(self.height // self.cell_size)
            ) for _y in range(self.width // self.cell_size)
        )

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
            mouse_pos = pg.mouse.get_pos()
            state_pos = tuple(p // self.cell_size for p in mouse_pos)
            self.create = not self.state[state_pos[0]][state_pos[1]]
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

    def on_loop(self):
        if self.play:
            self._clock.tick(self.framerate)
            self.state = twod.next_state(self.state, self.rule)
            if self.one_step:
                self.play = False
                self.one_step = False
            return
        self._clock.tick(self.framerate * 2)
        if self.create is not None:
            mouse_pos = pg.mouse.get_pos()
            state_pos = tuple(p // self.cell_size for p in mouse_pos)
            n_state = int(self.create)
            self.state = tuple(
                tuple(
                    self.state[y][x] if (y, x) != state_pos else n_state
                    for x in range(self.height // self.cell_size)
                ) for y in range(self.width // self.cell_size)
            )

    def render_state(self):
        background = self.WHITE
        if not self.play:
            background = self.GREY
        self._display_surf.fill(background)
        for x in range(self.height // self.cell_size):
            for y in range(self.width // self.cell_size):
                if self.state[y][x]:
                    x_loc = x * self.cell_size
                    y_loc = y * self.cell_size
                    self._display_surf.fill(
                        self.BLACK,
                        rect=(y_loc, x_loc, self.cell_size, self.cell_size)
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
                        help='The rule of the game.')
    parser.add_argument('density', nargs='?', type=float,
                        help='The starting density of the game.')
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
