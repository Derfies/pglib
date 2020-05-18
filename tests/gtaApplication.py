import os
import sys
import math
import random
#from functools import partial

import pyglet
import nodebox.graphics as nbg

import pglib
from pglib.draw.pyglet import utils as pygutils
from pglib.geometry.point import Point2d
from pglib.draw.pyglet.drawables import Rect
#from pygprim.context import line, ellipse
from pglib import utils
from pglib.region import Region
from pglib.randomregions import random_regions
from pglib.const import *
from pglib.weights import SineWeight
from nodeboxapplication import NodeBoxApplication

from sweepTest01 import Sweep


GRID_SPACING = 10
WIDTH = 1080
HEIGHT = 1080


window = pyglet.window.Window(width=WIDTH, height=HEIGHT)

@window.event
def on_draw():
    window.clear()

    grid = 40
    pRegion = Region(0, 0, WIDTH / grid, HEIGHT / grid)
    sineWeight = SineWeight(1, invert=True)
    regions = random_regions(pRegion, 5, 20, 30, intersect=True, center_weight=sineWeight)


    for region in regions:
        #colour = pglib.utils.get_random_colour(a=0.05)
        #rectArgs = [region.x1 * grid, region.y1 * grid, region.x2 * grid, region.y2 * grid]
        #drawFns.append(partial(rectangle, *rectArgs, fill=colour, stroke=(1, 0, 0, 0.75)))
        Rect(
            Point2d(region.x1 * grid_spacing, region.y1 * grid_spacing),
            Point2d(region.x2 * grid_spacing, region.y2 * grid_spacing),
            colour=None,
            line_colour=utils.get_random_colour(1),
            line_width=4,
        ).draw()
    #'''
    # position = regions[-1].x1, regions[-1].y1
    # sweep = Sweep(regions, grid)
    # draws, verts = sweep.doIt(position)
    # #drawFns.extend(draws)

    # # Find the "corners".
    # lr = sorted(verts, key=lambda v: math.sqrt(pow(v.x, 2) + pow(v.y, 2)))
    # #drawFns.append(partial(nbg.ellipse, lr[0].x * grid, lr[0].y * grid, 25, 25, fill=(0,1,0,1)))
    # #drawFns.append(partial(nbg.ellipse, lr[-1].x * grid, lr[-1].y * grid, 25, 25, fill=(0,1,0,1)))
    # ud = sorted(verts, key=lambda v: math.sqrt(pow(v.x, 2) + pow(HEIGHT / grid - v.y, 2)))
    # #drawFns.append(partial(nbg.ellipse, ud[0].x * grid, ud[0].y * grid, 25, 25, fill=(0,1,0,1)))
    # #drawFns.append(partial(nbg.ellipse, ud[-1].x * grid, ud[-1].y * grid, 25, 25, fill=(0,1,0,1)))

    # # Do outer "city limits":
    # verts = sorted(verts, key=lambda v: (v.x, v.y))
    # vs = sweep.getOutline(verts[0])
    # # for v in vs:
    # #     drawFns.append(partial(nbg.ellipse, v.x * grid, v.y * grid, 20, 20, fill=(1,0,0,1)))
    # # for i in range(len(vs) - 1):
    # #     drawFns.append(partial(nbg.line, vs[i].x * grid, vs[i].y * grid, vs[i + 1].x * grid, vs[i + 1].y * grid, strokewidth=10, stroke=(1,0,0,1)))
    # # drawFns.append(partial(nbg.line, vs[0].x * grid, vs[0].y * grid, vs[-1].x * grid, vs[-1].y * grid, strokewidth=10, stroke=(1,0,0,1)))

    # assert len(vs), 'No outline!'

    # print 'outline:', len(vs)

    # #dw = DrunkardsMeshWalk(vs)
    # vs2 = vs[:]
    # for i in range(10):

    #     vs = sweep.walk(vs2)
    #     #dw.verts.extend(vs)
    #     #print grid
    #     #c = (0,0,1,1)
    #     ##for v in vs:
    #     #    ellipse(v.x * grid, v.y * grid, 20, 20, fill=c)
    #     #for i in range(len(vs) - 1):
    #     #    line(vs[i].x * grid, vs[i].y * grid, vs[i + 1].x * grid, vs[i + 1].y * grid, strokewidth=10, stroke=c)

pyglet.app.run()