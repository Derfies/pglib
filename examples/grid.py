import logging

from pglib.draw.pyglet.appbase import AppBase
from pglib.generators.grid import Grid
from pglib.generators.image import Image
from pglib.node import Node
from pglib.region import Region
from pglib.samplers.constant import Constant
from pglib.samplers.range import Range


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 16
WIDTH = 30
HEIGHT = 30
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING


# Create tree.
root = Node('root', Grid(Range(1, 3), Range(1, 3), padding=Constant(1)))
root.add_child(Node('all', Image('pillar_bottom')))

# Add some input data.
root.add_input(Region(0, 0, WIDTH, HEIGHT))

# Create test app and run.
app = AppBase(root, GRID_SPACING, WINDOW_WIDTH, WINDOW_HEIGHT)
app.run()