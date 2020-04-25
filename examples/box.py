import logging

from pglib.draw.pyglet.appbase import AppBase
from pglib.node import Node
from pglib.region import Region
from pglib.generators.row import Row as RowGenerator
from pglib.generators.column import Column as ColumnGenerator
from pglib.generators.box import Box
from pglib.generators.bsp import Bsp
from pglib.generators.image import Image
from pglib.generators.grid import Grid
from pglib.selectors.all import All
from pglib.selectors.column import Column as ColumnSelector
from pglib.samplers.randomchoice import RandomChoice
from pglib.samplers.constant import Constant
from pglib.samplers.range import Range
from pglib.const import Axis


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 16
WIDTH = 30
HEIGHT = 30
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING

# Create tree.
root_node = Node('root', Bsp(
    RandomChoice([Axis.X, Axis.Y]),
    padding=Constant(0)
), recurse_while_fn=lambda i, r: r.width > 10 and r.height > 10)

next_node = Node('all', Box(padding=Constant(0)))
root_node.add_child(next_node)


#next_node.add_child(Node('all', Image('pillar_bottom')))
#root_node.add_child(Node('all', Image('pillar_bottom')))
#
# next_node = Node('all', Box(
#     padding_y2=Range(7)
# ), All())
# root_node.add_child(next_node)
#
# column = Node('all', ColumnGenerator(1), ColumnSelector())
# next_node.add_child(column)
# column.add_child(Node('bottom', Image('pillar_bottom')))
# column.add_child(Node('middle', Image('pillar_middle')))
# column.add_child(Node('top', Image('pillar_top')))

# Add some data and evaluate the root node.
root_node.inputs.append(Region(0, 0, WIDTH, HEIGHT))
root_node.evaluate()

# Create test app and run.
app = AppBase(root_node, GRID_SPACING, WINDOW_WIDTH, WINDOW_HEIGHT)
app.run()