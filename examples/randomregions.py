import logging

import pyglet
from pyglet import gl
from pyglet.window import key

from pglib import pygutils
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

# Run main loop and draw.
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
gl.glEnable(pyglet.gl.GL_BLEND)
gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.F5:
        logger.info('')
        root_node.evaluate()


@window.event
def on_draw():
    window.clear()
    pygutils.grid(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SPACING, (0.25, 0.25, 0.25, 1))
    pygutils.draw(root_node, GRID_SPACING)


pyglet.app.run()