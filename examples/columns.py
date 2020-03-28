import logging

import pyglet
from pyglet import gl
from pyglet.window import key

from pglib import pygutils
from pglib.node import Node
from pglib.region import Region
from pglib.generators.row import Row as RowGenerator
from pglib.generators.column import Column as ColumnGenerator
from pglib.generators.box import Box
from pglib.generators.image import Image
from pglib.selectors.all import All
from pglib.selectors.column import Column as ColumnSelector
from pglib.samplers.constant import Constant
from pglib.samplers.range import Range


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 16
WIDTH = 20
HEIGHT = 11
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING

# Create tree.
root_node = Node('root', RowGenerator(
    Constant(1),
    padding=Constant(1)
), All())

next_node = Node('all', Box(
    padding_y2=Range(7)
), All())
root_node.add_child(next_node)

column = Node('all', ColumnGenerator(1), ColumnSelector())
next_node.add_child(column)
column.add_child(Node('bottom', Image('pillar_bottom')))
column.add_child(Node('middle', Image('pillar_middle')))
column.add_child(Node('top', Image('pillar_top')))

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