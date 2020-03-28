import logging

import pyglet
from pyglet.window import key

from pglib import pygutils
from pglib.node import Node
from pglib.region import Region
from pglib.generators.bspregions import BspRegions


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 10
MIN_LEAF_SIZE = 6
MAX_LEAF_SIZE = 20
WIDTH = 64 * GRID_SPACING
HEIGHT = 48 * GRID_SPACING


# Create root node and add some data.
root_node = Node('root', BspRegions(MIN_LEAF_SIZE, MAX_LEAF_SIZE))
root_node.data.append(Region(0, 0, 64, 48))
root_node.evaluate()

# Run main loop and draw.
window = pyglet.window.Window(WIDTH, HEIGHT)


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.F5:
        root_node.evaluate()


@window.event
def on_draw():
    window.clear()
    pygutils.grid(WIDTH, HEIGHT, GRID_SPACING, (0.25, 0.25, 0.25, 1))
    pygutils.draw(root_node, GRID_SPACING)
pyglet.app.run()