import os
import sys
if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))
test_dir = os.path.join(os.path.dirname(__file__), '..', 'tests')
if test_dir not in sys.path:
    sys.path.append(test_dir)

import logging

import pyglet

import pygutils
from pglib import utils
from pglib.node import Node
from pglib.region import Region
from pglib.generators.grid import Grid
from pglib.generators.column import Column
from pglib.selectors.random import Random
from pglib.selectors.chunk import Chunk
from pglib.selectors.half import Half
from pglib.selectors.column import Column as ColumnSelector


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 10
WIDTH = 640
HEIGHT = 480


# Create root node.
root_node = Node()
#root_node.data.append(Region(0, 0, 10, 20))
root_node.data.append(Region(0, 0, 10, 40))
root_node.data.append(Region(20, 0, 30, 30))
root_node.generator = Column(10)
root_node.selector = ColumnSelector()
root_node.selector.generator = Column(5)
root_node.evaluate()


window = pyglet.window.Window()

@window.event
def on_draw():
    window.clear()
    pygutils.grid(WIDTH, HEIGHT, GRID_SPACING, (0.25, 0.25, 0.25, 1))

    for node in root_node.children:
        #print 'top node:', node, len(node.data)
        for region in node.data:
            #print region
            pygutils.region_to_rect(
                region, 
                grid_spacing=GRID_SPACING, 
                stroke=utils.get_random_colour(),
                strokewidth=10,
            )

        for cnode in node.children:
            #print 'cnode:', cnode, 'num regions:', len(cnode.data)
            #print 'render cnode'
            for cregion in cnode.data:
                #print '   ', cregion
                pygutils.region_to_rect(
                    cregion, 
                    grid_spacing=GRID_SPACING, 
                    stroke=utils.get_random_colour(),
                    strokewidth=1,
                )
        

pyglet.app.run()