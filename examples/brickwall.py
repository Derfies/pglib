import logging

from pglib.draw.pyglet.appbase import AppBase
from pglib.generators.column import Column
from pglib.generators.image import Image
from pglib.generators.row import Row
from pglib.node import Node
from pglib.region import Region
from pglib.samplers.constant import Constant


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 10
WIDTH = 30
HEIGHT = 20
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING


# Create tree.
root = Node('root', Row(Constant(2), padding=Constant(1)))
node_a = Node('every_second', Column(Constant(6)))
node_b = Node('every_other', Column(Constant(6), padding_x1=Constant(3)))

root.add_child(node_a, lambda data: data[slice(0, len(data), 2)])
root.add_child(node_b, lambda data: data[slice(1, len(data), 2)])
node_a.add_child(Node('bottom', Image('pillar_bottom')))
node_b.add_child(Node('top', Image('pillar_top')))

# Add some input data.
root.add_input(Region(5, 0, WIDTH - 5, HEIGHT))

# Create test app and run.
app = AppBase(root, GRID_SPACING, WINDOW_WIDTH, WINDOW_HEIGHT)
app.run()