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
from pglib.selectors.random import Random
from pglib.selectors.chunk import Chunk


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 10
WIDTH = 640
HEIGHT = 480


#class GridOfGrids()


# First level
g = Grid(2, 2)
g.input_node = Node(Region(0, 0, 40, 40))
g.selector = Chunk(2)

# Second level
g2 = Grid(2, 2)
g.selector.set_generator('1', g2)
g.run()



window = pyglet.window.Window()

@window.event
def on_draw():
    window.clear()
    pygutils.grid(WIDTH, HEIGHT, GRID_SPACING, (0.25, 0.25, 0.25, 1))

    for node in g.output_nodes:
        pygutils.region_to_rect(
            node, 
            grid_spacing=GRID_SPACING, 
            stroke=utils.get_random_colour(),
            strokewidth=10,
        )

        for generator in g.selector.generators.values():
            for node in generator.output_nodes:
                pygutils.region_to_rect(
                    node, 
                    grid_spacing=GRID_SPACING, 
                    stroke=utils.get_random_colour(),
                    strokewidth=2,
                )
        

pyglet.app.run()