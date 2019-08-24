import os
import sys
import math
import random
from functools import partial

import nodebox.graphics as nbg

import pglib
from pglib.const import *
from pglib.weights import SineWeight
from nodeboxapplication import NodeBoxApplication

from sweepTest01 import Sweep


GRID_SPACING = 10
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 1080


class GtaApplication(NodeBoxApplication):

    def get_draw_functions(self):

        drawFns = []
        
        #dw = DrunkardsWalk(SCREEN_WIDTH / GRID_SPACING, SCREEN_HEIGHT / GRID_SPACING, maxIterations=100, stepLength=10)
        #dw.generateLevel()

        grid = 40
        pRegion = pglib.Region(0, 0, SCREEN_WIDTH / grid, SCREEN_HEIGHT / grid)
        sineWeight = SineWeight(1, invert=True)
        regions = pglib.random_regions(pRegion, 5, 20, 30, intersect=True, center_weight=sineWeight)
        
        for region in regions:
            colour = pglib.utils.get_random_colour(a=0.05)
            rectArgs = [region.x1 * grid, region.y1 * grid, region.x2 * grid, region.y2 * grid]
            #drawFns.append(partial(rectangle, *rectArgs, fill=colour, stroke=(1, 0, 0, 0.75)))
        #'''
        position = regions[-1].x1, regions[-1].y1
        sweep = Sweep(regions, grid)
        draws, verts = sweep.doIt(position)
        drawFns.extend(draws)

        # Find the "corners".
        lr = sorted(verts, key=lambda v: math.sqrt(pow(v.x, 2) + pow(v.y, 2)))
        drawFns.append(partial(nbg.ellipse, lr[0].x * grid, lr[0].y * grid, 25, 25, fill=(0,1,0,1)))
        drawFns.append(partial(nbg.ellipse, lr[-1].x * grid, lr[-1].y * grid, 25, 25, fill=(0,1,0,1)))
        ud = sorted(verts, key=lambda v: math.sqrt(pow(v.x, 2) + pow(SCREEN_HEIGHT / grid - v.y, 2)))
        drawFns.append(partial(nbg.ellipse, ud[0].x * grid, ud[0].y * grid, 25, 25, fill=(0,1,0,1)))
        drawFns.append(partial(nbg.ellipse, ud[-1].x * grid, ud[-1].y * grid, 25, 25, fill=(0,1,0,1)))

        # Do outer "city limits":
        verts = sorted(verts, key=lambda v: (v.x, v.y))
        vs = sweep.getOutline(verts[0])
        for v in vs:
            drawFns.append(partial(nbg.ellipse, v.x * grid, v.y * grid, 20, 20, fill=(1,0,0,1)))
        for i in range(len(vs) - 1):
            drawFns.append(partial(nbg.line, vs[i].x * grid, vs[i].y * grid, vs[i + 1].x * grid, vs[i + 1].y * grid, strokewidth=10, stroke=(1,0,0,1)))
        drawFns.append(partial(nbg.line, vs[0].x * grid, vs[0].y * grid, vs[-1].x * grid, vs[-1].y * grid, strokewidth=10, stroke=(1,0,0,1)))
      
        assert len(vs), 'No outline!'

        print 'outline:', len(vs)

        #dw = DrunkardsMeshWalk(vs)
        vs2 = vs[:]
        for i in range(10):

            vs = sweep.walk(vs2)
            #dw.verts.extend(vs)

            c = (0,0,1,1)
            for v in vs:
                drawFns.append(partial(nbg.ellipse, v.x * grid, v.y * grid, 20, 20, fill=c))
            for i in range(len(vs) - 1):
                drawFns.append(partial(nbg.line, vs[i].x * grid, vs[i].y * grid, vs[i + 1].x * grid, vs[i + 1].y * grid, strokewidth=10, stroke=c))
        #'''

        return drawFns


if __name__ == '__main__':
    GtaApplication(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING)