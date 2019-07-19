from pglib import utils, Region, bsp_regions
from nodeboxapplication import NodeBoxApplication


MIN_LEAF_SIZE = 6
MAX_LEAF_SIZE = 20


class App(NodeBoxApplication):
    
    def get_draw_functions(self):
        p_region = Region(0, 0, self.width / self.grid_spacing, self.height / self.grid_spacing)
        return [
            self.region_to_rect(region, fill=utils.get_random_colour(a=1))
            for region in bsp_regions(p_region, MIN_LEAF_SIZE, MAX_LEAF_SIZE)
        ]


if __name__ == '__main__':

    GRID_SPACING = 10
    SCREEN_WIDTH = 64 * GRID_SPACING
    SCREEN_HEIGHT = 48 * GRID_SPACING

    App(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING)