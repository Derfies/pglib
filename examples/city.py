import logging

from pglib.const import Axis
from pglib.draw.pyglet.appbase import AppBase
from pglib.generators.bsp import Bsp
from pglib.generators.grid import Grid
from pglib.generators.regionbase import RegionBase
from pglib.node import Node
from pglib.region import Region
from pglib.samplers.choice import Choice
from pglib.samplers.constant import Constant
from pglib.samplers.range import Range


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 10
WIDTH = 100
HEIGHT = 100
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING


# Create tree.
block = Node('block', Grid(Range(2, 4), Range(2, 4)))
footpath = Node('footpath', RegionBase(padding=Constant(1)))
building = Node('footpath', Bsp(Choice([Axis.X, Axis.Y])), recurse_while_fn=lambda i, r: r.data.width > 5 and r.data.height > 5)

block.add_child(footpath)
footpath.add_child(building)

# Add some input data.
block.add_input(Region(0, 0, WIDTH, HEIGHT))

# Create test app and run.
app = AppBase(block, GRID_SPACING, WINDOW_WIDTH, WINDOW_HEIGHT)
app.run()