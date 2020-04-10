import logging

from pglib.draw.pyglet.appbase import AppBase
from pglib.node import Node
from pglib.region import Region
from pglib.samplers.range import Range
from pglib.generators.randomregions import RandomRegions


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 10
WIDTH = 64
HEIGHT = 48
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING


# Create tree.
root_node = Node('root', RandomRegions(Range(5, 10), Range(5, 10), 200))

# Add some data and evaluate the root node.
root_node.inputs.append(Region(0, 0, WIDTH, HEIGHT))
root_node.evaluate()

# Create test app and run.
app = AppBase(root_node, GRID_SPACING, WINDOW_WIDTH, WINDOW_HEIGHT)
app.run()