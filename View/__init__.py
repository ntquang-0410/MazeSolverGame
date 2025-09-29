from pygame.examples.moveit import HEIGHT

from View.node_cell import Node_Cell

import pygame as pg

WIDTH_VIEW = 1000
HEIGHT_VIEW = 700

class View:
    def __init__(self, width, height):
        pg.init()
        self.screen = pg.display.set_mode((width, height))
        pg.display.set_caption("MAZE SOLVER GAME")
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont(None, 36)

    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(text_surface, (x, y))

    def clear(self):
        self.screen.fill((0, 0, 0))

    def update(self):
        pg.display.flip()
        self.clock.tick(60)

    def quit(self):
        pg.quit()


if __name__ == "__main__":
    view = View(WIDTH_VIEW, HEIGHT_VIEW)
    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        view.clear()
        view.draw_text("Hello, MVC!", 0, 0)
        view.update()
    view.quit()