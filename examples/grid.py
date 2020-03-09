import os
import sys
if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))
import logging

import pyglet

import pygutils
from pglib import utils
from pglib.node import Node
from pglib.region import Region
from pglib.generators.grid import Grid
from pglib.selectors.random import Random


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


GRID_SPACING = 10
WIDTH = 640
HEIGHT = 480


#class GridOfGrids()


rnd_sel = Random(Grid)
g = Grid(2, 2, selector=rnd_sel)
g.input_node = Node(Region(0, 0, 40, 40))
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

        for generator in g.selector.generators:
            for node in generator.output_nodes:
                pygutils.region_to_rect(
                    node, 
                    grid_spacing=GRID_SPACING, 
                    stroke=utils.get_random_colour(),
                    strokewidth=2,
                )
        

pyglet.app.run()