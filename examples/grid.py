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
from pglib.generators.column import Column as ColumnGenerator
from pglib.generators.singleregion import SingleRegion
from pglib.generators.randomregions import RandomRegions
from pglib.generators.image import Image
from pglib.selectors.random import Random
from pglib.selectors.chunk import Chunk
from pglib.selectors.half import Half
from pglib.selectors.all import All
from pglib.selectors.column import Column as ColumnSelector
from pglib.samplers.range import Range


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
root_node = Node('root', RandomRegions(Range(10, 10), Range(10, 80), 200), All())

next_node = Node('all', ColumnGenerator(10), ColumnSelector())
root_node.add_child(next_node)

next_node.add_child(Node('bottom', Image('pillar_bottom')))
next_node.add_child(Node('middle', Image('pillar_middle')))
next_node.add_child(Node('top', Image('pillar_top')))




root_node.data.append(Region(0, 0, 160, 80))
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
            #print 'cnode:', cnode, 'num children:', len(cnode.data)
            #print 'render cnode'
           # for cregion in cnode.data:

                # if not hasattr(cregion, 'sprite'):
                #     #print '   ', cregion.x1, cregion.y1
                #     pygutils.region_to_rect(
                #         cregion, 
                #         grid_spacing=GRID_SPACING, 
                #         stroke=utils.get_random_colour(),
                #         strokewidth=1,
                #         #fill=node.generator.colour
                #     )
                # else:
                #     pyglet.gl.glColor4f(1, 1, 1, 1)
                #     cregion.sprite_image.texture.width = cregion.width * GRID_SPACING
                #     cregion.sprite_image.texture.height = cregion.height * GRID_SPACING
                #     cregion.sprite_image.blit(cregion.x1 * GRID_SPACING, cregion.y1 * GRID_SPACING)

            for ccnode in cnode.children:
                #print 'ccnode:', ccnode, 'num children:', len(ccnode.data)
                #print 'render cnode'
                for cregion in ccnode.data:

                    if not hasattr(cregion, 'sprite'):
                        #print '   ', cregion.x1, cregion.y1
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