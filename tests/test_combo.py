from functools import partial

import nodebox.graphics as nbg

from pglib import utils, Region, random_regions, drunkards_walk
from nodeboxapplication import NodeBoxApplication


class App(NodeBoxApplication):
    
    def get_draw_functions(self):
        p_region = Region(0, 0, self.width / self.grid_spacing, self.height / self.grid_spacing)
        
        draw_fns = []
        for region in random_regions(p_region, 15, 20, 300, False, value=1):
            drunkards_walk(region)
            colour = utils.get_random_colour(a=1)
            for x, row in enumerate(region.matrix):
                for y, cell in enumerate(region.matrix[x]):
                    if cell:
                        x1 = (region.x1 + x) * self.grid_spacing
                        y1 = (region.y1 + y) * self.grid_spacing
                        size = self.grid_spacing
                        draw_fns.append(partial(nbg.rect, *[x1, y1, size, size], fill=colour))
        return draw_fns


if __name__ == '__main__':

    GRID_SPACING = 10
    SCREEN_WIDTH = 64 * GRID_SPACING
    SCREEN_HEIGHT = 48 * GRID_SPACING

    App(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING)