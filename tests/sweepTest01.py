import os
import sys
import random
from collections import deque
from functools import partial

from geometry import Point2d
import nodebox.graphics as nbg

import pglib
from pglib.const import *
from pglib.region import Region
from nodeboxapplication import NodeBoxApplication


GRID_SPACING = 10
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720

CLOCKWISE_DIRS = [
    POS_Y,
    POS_X,
    NEG_Y,
    NEG_X
]


class Vertex(Point2d):

    def __init__(self, region, *args, **kwargs):
        super(Vertex, self).__init__(*args, **kwargs)

        self.region = region
        self.edges = {}


class Sweep(object):
    
    def __init__(self, regions, scale=1):
        self.regions = regions
        self.scale = scale

    def getOutline(self, startVert):

        verts = []
        prevDir = None
        vert = startVert
        outlined = False
        while not outlined:

            # Rotate directions so that they start using the direction we last took.
            dirs = deque(CLOCKWISE_DIRS[:])
            if prevDir is not None:
                dirs.rotate(-list(dirs).index(prevDir.opposite) - 1)

            # Test for next available direction.
            nextDir = None
            for dir_ in dirs:
                if dir_ in vert.edges:
                    nextDir = dir_
                    break
            else:
                raise Exception('Cannot find next vertex!')

            nextVert = vert.edges[nextDir]
            verts.append(nextVert)
            vert, prevDir = nextVert, nextDir
            outlined = vert == startVert

        return verts

    def getRegionsEdges(self, regions, getEdgeFn, sortAttr):
        edges = {}
        for region in regions:
            for rEdge in getEdgeFn(region):
                edges.setdefault(rEdge, []).append(region)
        for edge in edges:
            edges[edge] = sorted(edges[edge], key=lambda r: getattr(r, sortAttr))
        return edges

    def getEventVertGroups(self, t, vEdges, hEdges):
        regions = vEdges[t]

        # Split region edges into groups that can represent a contiguous vertical 
        # edge.
        vertGroups = [[]]
        maxEdge = regions[0].y2
        for r in regions:
            if r.y1 > maxEdge:
                vertGroups.append([])
            vertGroups[-1].extend([Vertex(r,t, r.y1), Vertex(r, t, r.y2)] )
            maxEdge = max(maxEdge, r.y2)

        # Sort verts then look for any intersections with open regions. 
        # Where there is an intersection insert a new vertex.
        for i, verts in enumerate(vertGroups):
            for j in range(len(verts) - 1):
                for edge, regions in hEdges.items():
                    if verts[j].y <= edge <= verts[j + 1].y:

                        # Add a vertex, or update the region of an existing one.
                        v = Vertex(regions[0], t, edge)
                        if v in vertGroups[i]:
                            vi = vertGroups[i].index(v)
                            vertGroups[i][vi].region = regions[-1]
                        else:
                            vertGroups[i].append(v)

            # Remove duplicates.
            # TO DO: Figure out why we'r getting duplicates in the firstt place.
            vertGroups[i] = sorted(list(set(vertGroups[i])), key=lambda v: v.y)   
        return vertGroups

    def doIt(self, position=None, direction=POS_Y):
        """
        Note - we "end" a region then perform a bunch of intersection checks
        before we "start" a region on the same vertical edge. This stops region 
        edges on the same X value from intersecting each other.
        """
        # Index all regions by their vertical edges.
        vEdges = self.getRegionsEdges(self.regions, Region.getXEdges, 'y1')

        allVerts = []
        openRegions = []
        openVerts = {}
        for t in sorted(vEdges):

            # If this event represents a region ending, remove it from the list
            # of open regions.
            for region in vEdges[t]:
                if t == region.x2:
                    openRegions.remove(region)

            # Index regions that are currently open by their horizintal edges.
            hEdges = self.getRegionsEdges(openRegions, Region.getYEdges, 'x1')

            # Build edges.
            for verts in self.getEventVertGroups(t, vEdges, hEdges):

                # Vertical edges.
                for j in range(len(verts) - 1):
                    v1, v2 = verts[j], verts[j + 1]
                    v1.edges[POS_Y], v2.edges[NEG_Y] = v2, v1

                # Horizontal edges.
                for vert in verts:
                    if vert.y not in openVerts:
                        continue
                    v1, v2 = openVerts[vert.y], vert
                    if v1.region == v2.region or v1.region.x2 >= v2.region.x1:
                        v1.edges[POS_X], v2.edges[NEG_X] = v2, v1

                openVerts.update({v.y: v for v in verts})
                allVerts.extend(verts)

            # If this event represents a region starting, add it to the list of
            # open regions.
            for region in vEdges[t]:
                if t == region.x1:
                    openRegions.append(region)

        # for vert in allVerts:
        #     vert.x += random.uniform(0, 1)
        #     vert.y += random.uniform(0, 1)

        draws = []
        for v in allVerts:
            draws.append(partial(nbg.ellipse, v.x * self.scale, v.y * self.scale, 10, 10, fill=(0,1,0,1)))
            for edge in v.edges.values():
                v1 = v
                v2 = edge
                c = (0.5,0.5,0.5,1)#getRandomColour(1)
                draws.append(partial(nbg.line, v1.x * self.scale, v1.y * self.scale, v2.x * self.scale, v2.y * self.scale, strokewidth=5, stroke=c))
            #print v, {k: str(v) for k, v in v.edges.items()}

        

        return draws, allVerts

    def walk(self, startVerts):
        verts = []

        # Randomise a start vert that has more than two edges.
        try:
            #vert = self.getStartVert()
            fverts = filter(lambda v: len(v.edges) > 2, startVerts)
            vert = fverts[random.randint(0, len(fverts) - 1)]
        except Exception, e:
           print e
           return []

        verts.append(vert)
        try:
            #mainDir = dir_ = self.getStartDirection(vert)
            edges = filter(lambda e: vert.edges[e] not in startVerts, vert.edges)
            mainDir = dir_ = edges[random.randint(0, len(edges) - 1)]

        except Exception, e:
            print e
            print vert
            return verts
        vert = vert.edges[dir_]
        verts.append(vert)


        i = 0
        prevDir = dir_
        while True:

            # Don't backtrack.
            dirs_ = vert.edges.keys()
            if prevDir is not None:
                dirs_.remove(prevDir.opposite)
            dir_ = mainDir
            if dir_ not in dirs_:

                if len(dirs_) > 1 and mainDir.opposite in dirs_:
                    print 'TRYING NOT TO GO BACKWARDS'
                    dirs_.remove(mainDir.opposite)

                dir_ = pglib.utils.get_random_direction(dirs_)

            vert = vert.edges[dir_]
            verts.append(vert)
            
            prevDir = dir_

            i += 1
            if vert in startVerts or i > 100:
                break

        return verts


class Application(NodeBoxApplication):

    def getDrawFunctions(self):
        drawFns = []

        rs = []
        rs.append(pglib.Region(5, 5, 25, 15))
        rs.append(pglib.Region(20, 5, 40, 15))
        rs.append(pglib.Region(35, 5, 55, 15))


        rs.append(pglib.Region(0, 0, 10, 10))
        rs.append(pglib.Region(8, 8, 18, 18))
        rs.append(pglib.Region(16, 0, 26, 10))

        rs.append(pglib.Region(10, 28, 20, 38))
        rs.append(pglib.Region(10, 30, 20, 40))
        rs.append(pglib.Region(10, 32, 20, 42))
        rs.append(pglib.Region(0, 35, 10, 45))

        rs.append(pglib.Region(0, 0, 10, 10))
        rs.append(pglib.Region(5, 5, 15, 15))

        rs.append(pglib.Region(15, 35, 25, 45))

        rs.append(pglib.Region(60, 0, 70, 70))
        rs.append(pglib.Region(65, 20, 75, 30))


        rs.append(pglib.Region(0, 50, 10, 60))
        rs.append(pglib.Region(5, 50, 15, 60))


        sweep = Sweep(rs, self.gridSpacing)
        draws, verts = sweep.doIt()
        drawFns.extend(draws)

        grid = self.gridSpacing
        for region in rs:
            colour = getRandomColour(a=0.1)
            rectArgs = [region.x1 * grid, region.y1 * grid, region.x2 * grid, region.y2 * grid]
            #drawFns.append(partial(rectangle, *rectArgs, fill=colour, stroke=(1, 0, 0, 1)))

        return drawFns


if __name__ == '__main__':
    NodeBoxApplication(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SPACING)