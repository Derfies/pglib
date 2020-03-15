import os
import sys
if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))
test_dir = os.path.join(os.path.dirname(__file__), '..', 'tests')
if test_dir not in sys.path:
    sys.path.append(test_dir)

import logging

import pyglet
from pyglet import gl

import pygutils
from pglib import utils
from pglib.node import Node
from pglib.region import Region
from pglib.generators.grid import Grid
from pglib.generators.column import Column
from pglib.generators.singleregion import SingleRegion
from pglib.generators.image import Image
from pglib.selectors.random import Random
from pglib.selectors.chunk import Chunk
from pglib.selectors.half import Half
from pglib.selectors.column import Column as ColumnSelector


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 10
WIDTH = 1600
HEIGHT = 800


#pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST
#pyglet.image.Texture.default_min_filter = pyglet.gl.GL_NEAREST
gl.glEnable(gl.GL_TEXTURE_2D)
gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)



# Create root node and add some data.
root_node = Node()
root_node.data.append(Region(10, 10, 20, 20))
root_node.data.append(Region(30, 10, 40, 30))
root_node.data.append(Region(50, 10, 60, 40))
root_node.data.append(Region(70, 10, 80, 50))
root_node.data.append(Region(90, 10, 100, 60))

root_node.generator = Column(10)
root_node.selector = ColumnSelector()
root_node.selector.map = {
    'bottom': Image('pillar_bottom'),
    'middle': Image('pillar_middle'),
    'top': Image('pillar_top'),
}
root_node.evaluate()


window = pyglet.window.Window(WIDTH, HEIGHT)

@window.event
def on_draw():
    window.clear()
    pygutils.grid(WIDTH, HEIGHT, GRID_SPACING, (0.25, 0.25, 0.25, 1))

    for node in root_node.children:
        #print 'top node:', node, len(node.data)
        # for region in node.data:
        #     #print region
        #     pygutils.region_to_rect(
        #         region, 
        #         grid_spacing=GRID_SPACING, 
        #         stroke=utils.get_random_colour(),
        #         strokewidth=10,
        #     )

        for cnode in node.children:
            #print 'cnode:', cnode, 'num regions:', len(cnode.data)
            #print 'render cnode'
            for cregion in cnode.data:

                if not hasattr(cregion, 'sprite'):
                    #print '   ', cregion
                    pygutils.region_to_rect(
                        cregion, 
                        grid_spacing=GRID_SPACING, 
                        stroke=utils.get_random_colour(),
                        strokewidth=1,
                        #fill=node.generator.colour
                    )
                else:
                    pyglet.gl.glColor4f(1, 1, 1, 1)
                    cregion.sprite_image.texture.width = cregion.width * GRID_SPACING
                    cregion.sprite_image.texture.height = cregion.height * GRID_SPACING
                    cregion.sprite_image.blit(cregion.x1 * GRID_SPACING, cregion.y1 * GRID_SPACING)
        

pyglet.app.run()