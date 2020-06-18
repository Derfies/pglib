import enum

import pyglet
import networkx as nx
import matplotlib.pyplot as plt
from intervaltree import IntervalTree, Interval

from pglib.geometry.rect import Rect
from pglib.geometry.vector import Vector2
from pglib.draw.pyglet import utils
from pglib.draw.pyglet.drawables import Grid, Circle


GRID_SPACING = 10
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720


class EventType(enum.Enum):

    BEGIN = 0
    END = 1


class Event(object):

    def __init__(self, type_, rect):
        self.type = type_
        self.rect = rect





rs = []

# One
# rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))

# Two x align
# rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))
# rs.append(Rect(Vector2(0, 20), Vector2(10, 30)))

# Two x align overlap
# rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))
# rs.append(Rect(Vector2(0, 5), Vector2(10, 15)))

# Two y align
# rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))
# rs.append(Rect(Vector2(20, 0), Vector2(30, 10)))

# Two y align overlap
# rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))
# rs.append(Rect(Vector2(5, 0), Vector2(15, 10)))

# Two corner touching
# rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))
# rs.append(Rect(Vector2(10, 10), Vector2(20, 20)))

# Two corner overlap
# rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))
# rs.append(Rect(Vector2(5, 5), Vector2(15, 15)))

# 2 x 2 grid
# rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))
# rs.append(Rect(Vector2(0, 10), Vector2(10, 20)))
# rs.append(Rect(Vector2(10, 10), Vector2(20, 20)))
# rs.append(Rect(Vector2(10, 0), Vector2(20, 10)))


rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))
rs.append(Rect(Vector2(5, 5), Vector2(15, 15)))
rs.append(Rect(Vector2(15, 8), Vector2(20, 18)))
rs.append(Rect(Vector2(25, 8), Vector2(30, 18)))
rs.append(Rect(Vector2(14, 5), Vector2(25, 15)))

rs.append(Rect(Vector2(5, 5), Vector2(25, 15)))

rs.append(Rect(Vector2(5, 8), Vector2(25, 18)))


rs.append(Rect(Vector2(20, 5), Vector2(40, 15)))
rs.append(Rect(Vector2(20, 10), Vector2(40, 20)))
rs.append(Rect(Vector2(35, 5), Vector2(55, 15)))


rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))
rs.append(Rect(Vector2(8, 8), Vector2(18, 18)))
rs.append(Rect(Vector2(16, 0), Vector2(26, 10)))

rs.append(Rect(Vector2(10, 28), Vector2(20, 38)))
rs.append(Rect(Vector2(10, 30), Vector2(20, 40)))
rs.append(Rect(Vector2(10, 32), Vector2(20, 42)))
rs.append(Rect(Vector2(0, 35), Vector2(10, 45)))


rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))

rs.append(Rect(Vector2(5, 5), Vector2(15, 15)))

rs.append(Rect(Vector2(15, 35), Vector2(25, 45)))

rs.append(Rect(Vector2(60, 0), Vector2(70, 70)))
rs.append(Rect(Vector2(65, 20), Vector2(75, 30)))


rs.append(Rect(Vector2(0, 50), Vector2(10, 60)))
rs.append(Rect(Vector2(5, 50), Vector2(15, 60)))




events = {}
for rect in rs:
    events.setdefault(rect.p1.x, []).append(Event(EventType.BEGIN, rect))
    events.setdefault(rect.p2.x, []).append(Event(EventType.END, rect))

g = nx.Graph()
verts = []
tree = IntervalTree()
open_verts = {}
for t in sorted(events):

    print '\n@ t:', t

    # Collect intervals that begin and end.
    intervals = {EventType.BEGIN: set(), EventType.END: set()}
    for event in events[t]:
        interval = Interval(event.rect.p1.y, event.rect.p2.y, event.rect)
        intervals[event.type].add(interval)

    # Add vertical edges and ensure all overlapping sections are split, then
    # split intervals that intersect the main tree.
    t_tree = IntervalTree(intervals[EventType.BEGIN] | intervals[EventType.END])
    t_tree.split_overlaps()
    for interval in set(t_tree):
        for overlap in tree.overlap(interval):
            t_tree.slice(overlap.begin)
            t_tree.slice(overlap.end)

    # Every interval that was either started or sliced becomes an open vert that
    # expects an edge.
    for i in t_tree:
        g.add_edge((t, i.begin), (t, i.end))
        print 'vertical edge:', (t, i.begin), (t, i.end)
        verts.extend((Vector2(t, i.begin), Vector2(t, i.end)))

        # Connect to last one here
        # Consider collecting verts and putting this in a new loop to remove
        # duplicates
        if i.begin in open_verts:
            g.add_edge((open_verts[i.begin], i.begin), (t, i.begin))
            print 'horizontal edge (begin):', (open_verts[i.begin], i.begin), (t, i.begin)
        if i.end in open_verts:
            g.add_edge((open_verts[i.end], i.end), (t, i.end))
            print 'horizontal edge (end):', (open_verts[i.end], i.end), (t, i.end)

    for i in t_tree:
        print 'open vert: ({}, {})'.format(t, i.begin,)
        open_verts[i.begin] = t
        print 'open vert: ({}, {})'.format(t, i.end)
        open_verts[i.end] = t

    tree.update(intervals[EventType.BEGIN])

    # Build max x extend dict.
    rects = [i.data for i in tree]
    max_edges = {}
    for rect in rects:
        max_edges[rect.p1.y] = max(max_edges.get(rect.p1.y), rect.p2.x)
        max_edges[rect.p2.y] = max(max_edges.get(rect.p2.y), rect.p2.x)

    for y in open_verts.keys():
        if y in max_edges and t == max_edges[y]:
            print 'close vert: ({}, {}) because t == max_edges[y]'.format(max_edges[y], y)
            del open_verts[y]


    tree.difference_update(intervals[EventType.END])


pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
pyglet.gl.glBlendFunc(
    pyglet.gl.GL_SRC_ALPHA,
    pyglet.gl.GL_ONE_MINUS_SRC_ALPHA
)



grid = Grid(
    GRID_SPACING,
    Vector2(0, 0),
    Vector2(SCREEN_WIDTH, SCREEN_HEIGHT),
    colour=None,
    line_colour=(0.25, 0.25, 0.25, 1)
)

print '\nnum verts:', len(verts)

print 'nodes:', g.nodes
print 'edges:', g.edges

window = pyglet.window.Window(SCREEN_WIDTH, SCREEN_HEIGHT)

@window.event
def on_draw():
    window.clear()
    grid.draw()

    for r in rs:
        utils.rect_to_rect(r, GRID_SPACING).draw()

    for v in verts:
        Circle(8, v * GRID_SPACING, 6, colour=(1, 0, 0, 0)).draw()


pyglet.app.run()
#pos = nx.nx_agraph.graphviz_layout(g, prog='neato')
#print pos
pos = {
    node: node for node in g
}

#pos = nx.spring_layout(g)
nx.draw(g, pos=pos, width=8, alpha=0.5, edge_color='b')
nx.draw_networkx_labels(g, pos=pos, font_size=8)
plt.show()

