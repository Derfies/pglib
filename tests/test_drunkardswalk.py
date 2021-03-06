from functools import partial

import nodebox.graphics as nbg

from pglib import utils, Region, drunkards_walk
from nodeboxapplication import NodeBoxApplication


class App(NodeBoxApplication):
    
    def get_draw_functions(self):
        p_region = Region(0, 0, self.width / self.grid_spacing, self.height / self.grid_spacing, value=1)
        drunkards_walk(p_region)

        draw_fns = []
        for x, row in enumerate(p_region.matrix):
            for y, cell in enumerate(p_region.matrix[x]):
                if cell:
                    x1 = x * self.grid_spacing
                    y1 = y * self.grid_spacing
                    size = self.grid_spacing
                    draw_fns.append(partial(nbg.rect, *[x1, y1, size, size], fill=(1, 0, 0, 1)))
        return draw_fns


if __name__ == '__main__':

    GRID_SPACING = 10
    SCREEN_WIDTH = 64 * GRID_SPACING
    SCREEN_HEIGHT = 48 * GRID_SPACING

    App(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING)