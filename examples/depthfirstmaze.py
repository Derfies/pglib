import logging

from pglib.draw.pyglet.appbase import AppBase
from pglib.node import Node
from pglib.region import Region
from pglib.samplers.range import Range
from pglib.generators.randomregions import RandomRegions
from pglib.generators.depthfirstmaze import DepthFirstMaze
from pglib.generators.bspregions import BspRegions
from pglib.samplers.constant import Constant
from pglib.selectors.all import All


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 10
WIDTH = 63
HEIGHT = 47
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING


# Create tree.
root_node = Node('root', RandomRegions(Range(10, 20), Range(10, 20), 200), All())
next_node = Node('all', DepthFirstMaze(padding=Constant(1)))
root_node.add_child(next_node)

# Add some data and evaluate the root node.
root_node.inputs.append(Region(0, 0, WIDTH, HEIGHT))
root_node.evaluate()

# Create test app and run.
app = AppBase(root_node, GRID_SPACING, WINDOW_WIDTH, WINDOW_HEIGHT)
app.run()