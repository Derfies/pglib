import logging

from pglib.draw.pyglet.appbase import AppBase
from pglib.generators.recursivemaze import RecursiveMaze
from pglib.node import Node
from pglib.region import Region


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 10
WIDTH = 63
HEIGHT = 47
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING


# Create tree.
# TODO: Can this generator be implemented using the node's recursive function?
root_node = Node('root', RecursiveMaze())

# Add some input data.
root_node.add_input(Region(0, 0, WIDTH, HEIGHT))

# Create test app and run.
app = AppBase(root_node, GRID_SPACING, WINDOW_WIDTH, WINDOW_HEIGHT)
app.run()