import logging

from pglib.draw.pyglet.appbase import AppBase
from pglib.generators.column import Column
from pglib.generators.image import Image
from pglib.generators.regionbase import RegionBase
from pglib.generators.row import Row
from pglib.node import Node
from pglib.region import Region
from pglib.samplers.constant import Constant
from pglib.samplers.range import Range
from pglib.selectors.sequence import Sequence


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 16
WIDTH = 11
HEIGHT = 11
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING


# Create tree.
root = Node('root', Column(Constant(1), padding=Constant(1)))
column = Node('column', RegionBase(padding_y2=Range(7)))
sections = Node('sections', Row(Constant(1)), Sequence())
bot = Node('bot', Image('pillar_bottom'))
mid = Node('mid', Image('pillar_middle'))
top = Node('top', Image('pillar_top'))

root.add_child(column)
column.add_child(sections)
sections.add_child(bot, sections.selector.first)
sections.add_child(mid, sections.selector.middle)
sections.add_child(top, sections.selector.last)

# Add some input data.
root.add_input(Region(0, 0, WIDTH, HEIGHT))

# Create test app and run.
app = AppBase(root, GRID_SPACING, WINDOW_WIDTH, WINDOW_HEIGHT)
app.run()