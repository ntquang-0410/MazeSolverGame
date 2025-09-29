import Model
import Controller
import pygame as pg

WIDTH_VIEW = 250
HEIGT_VIEW = 250

class View:
    def __init__(self, width, height):
        pg.init()
        self.screen = pg.display.set_mode((width, height))
        pg.display.set_caption("MVC Pattern Example")
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
    view = View(WIDTH_VIEW, HEIGT_VIEW)
