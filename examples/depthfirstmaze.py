import logging

from pglib.draw.pyglet.appbase import AppBase
from pglib.generators.depthfirstmaze import DepthFirstMaze
from pglib.generators.randomregions import RandomRegions
from pglib.node import Node
from pglib.region import Region
from pglib.samplers.constant import Constant
from pglib.samplers.range import Range


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 10
WIDTH = 63
HEIGHT = 47
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING


# Create tree.
root = Node('root', RandomRegions(Range(10, 20), Range(10, 20), 200))
root.add_child(Node('maze', DepthFirstMaze(padding=Constant(1))))

# Add some input data.
root.add_input(Region(0, 0, WIDTH, HEIGHT))

# Create test app and run.
app = AppBase(root, GRID_SPACING, WINDOW_WIDTH, WINDOW_HEIGHT)
app.run()