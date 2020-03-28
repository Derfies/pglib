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
from pglib.generators.randomregions import RandomRegions
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



#pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST
#pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST


# Create root node and add some data.
row_generator = RowGenerator(
    Constant(1),
    #Range(1),
    padding=Constant(1)
)
root_node = Node('root', row_generator, All())

next_node = Node('all', Box(
    padding_y2=Range(5)
), All())

# # next_node = Node('all', ColumnGenerator(1), ColumnSelector())
root_node.add_child(next_node)


column = Node('all', ColumnGenerator(1), ColumnSelector())
next_node.add_child(column)
# column.add_child(Node('bottom', Image('pillar_bottom')))
# column.add_child(Node('middle', Image('pillar_middle')))
# column.add_child(Node('top', Image('pillar_top')))



root_node.data.append(Region(0, 0, WIDTH, HEIGHT))
root_node.evaluate()

# Run main loop and draw.
window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
# gl.glEnable(gl.GL_TEXTURE_2D)
# gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)


@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.F5:
        root_node.evaluate()


@window.event
def on_draw():
    window.clear()
    pygutils.grid(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SPACING, (0.25, 0.25, 0.25, 1))
    pygutils.draw(root_node, GRID_SPACING)
pyglet.app.run()