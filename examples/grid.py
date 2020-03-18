import logging

import pyglet
from pyglet import gl

from pglib import pygutils
from pglib.node import Node
from pglib.region import Region
from pglib.generators.row import Row as RowGenerator
from pglib.generators.column import Column as ColumnGenerator
from pglib.generators.randomregions import RandomRegions
from pglib.generators.image import Image
from pglib.selectors.all import All
from pglib.selectors.column import Column as ColumnSelector
from pglib.samplers.constant import Constant
from pglib.samplers.range import Range


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 10
WIDTH = 1600
HEIGHT = 800



#pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST
#pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST


# Create root node and add some data.
root_node = Node('root', RowGenerator(Constant(10), Range(1)), All())
next_node = Node('all', ColumnGenerator(10), ColumnSelector())
root_node.add_child(next_node)
next_node.add_child(Node('bottom', Image('pillar_bottom')))
next_node.add_child(Node('middle', Image('pillar_middle')))
next_node.add_child(Node('top', Image('pillar_top')))

root_node.data.append(Region(10, 10, 150, 70))
root_node.evaluate()

# Run main loop and draw.
window = pyglet.window.Window(WIDTH, HEIGHT)
# gl.glEnable(gl.GL_TEXTURE_2D)
# gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)


@window.event
def on_draw():
    window.clear()
    pygutils.grid(WIDTH, HEIGHT, GRID_SPACING, (0.25, 0.25, 0.25, 1))
    pygutils.draw(root_node, GRID_SPACING)
pyglet.app.run()