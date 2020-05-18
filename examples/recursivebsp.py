import logging

from pglib.const import Axis
from pglib.draw.pyglet.appbase import AppBase
from pglib.generators.bsp import Bsp
from pglib.generators.image import Image
from pglib.node import Node
from pglib.region import Region
from pglib.samplers.choice import Choice
from pglib.samplers.constant import Constant
from pglib.selectors.base import SelectionMode


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 16
WIDTH = 40
HEIGHT = 40
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING

# Create tree.
root = Node(
    'root',
    Bsp(Choice([Axis.X, Axis.Y])),
    recurse_while_fn=lambda i, r: r.data.width > 5 and r.data.height > 5 and i < 1
)
root.selector.mode = SelectionMode.DESCENDENTS
root.children.append(Node('next', Image('cross', padding=Constant(1))))

# Add some input data.
root.add_input(Region(0, 0, WIDTH, HEIGHT))

# Create test app and run.
app = AppBase(root, GRID_SPACING, WINDOW_WIDTH, WINDOW_HEIGHT)
app.run()