import logging

from pglib.draw.pyglet.appbase import AppBase
from pglib.node import Node
from pglib.region import Region
from pglib.generators.bspregions import BspRegions
from pglib.samplers.range import Range
from pglib.samplers.constant import Constant
from pglib.generators.box import Box
from pglib.selectors.all import All
from pglib.selectors.filter import Filter


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


MIN_LEAF_SIZE = 6
MAX_LEAF_SIZE = 20
GRID_SPACING = 10
WIDTH = 64
HEIGHT = 48
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING


# Create tree.
root_node = Node('root', BspRegions(
    Constant(20),
    padding=Range(5)
), Filter(Range(10), 2))
next_node = Node('filter', Box(
    padding_x1=Range(5),
    padding_x2=Range(5),
    padding_y1=Range(5),
    padding_y2=Range(5),
), All())
root_node.add_child(next_node)

# Add some data and evaluate the root node.
root_node.inputs.append(Region(0, 0, WIDTH, HEIGHT))
root_node.evaluate()

# Create test app and run.
app = AppBase(root_node, GRID_SPACING, WINDOW_WIDTH, WINDOW_HEIGHT)
app.run()