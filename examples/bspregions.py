import logging

from pglib.draw.pyglet.appbase import AppBase
from pglib.generators.bspregions import BspRegions
from pglib.node import Node
from pglib.region import Region
from pglib.samplers.range import Range


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


MIN_LEAF_SIZE = 6
MAX_LEAF_SIZE = 20
GRID_SPACING = 10
WIDTH = 64
HEIGHT = 48
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING


# TODO: Port remaining bspregion stuff to bsp
# Create tree.
root = Node('root', BspRegions(Range(MIN_LEAF_SIZE, MAX_LEAF_SIZE), padding=Range(5)))

# Add some input data.
root.add_input(Region(0, 0, WIDTH, HEIGHT))

# Create test app and run.
app = AppBase(root, GRID_SPACING, WINDOW_WIDTH, WINDOW_HEIGHT)
app.run()