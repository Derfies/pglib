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

# rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))
# rs.append(Rect(Vector2(5, 5), Vector2(15, 15)))
rs.append(Rect(Vector2(15, 8), Vector2(20, 18)))
# rs.append(Rect(Vector2(15, 5), Vector2(25, 15)))
#
#
# rs.append(Rect(Vector2(5, 5), Vector2(25, 15)))
rs.append(Rect(Vector2(5, 8), Vector2(25, 18)))
# rs.append(Rect(Vector2(20, 5), Vector2(40, 15)))
# rs.append(Rect(Vector2(20, 10), Vector2(40, 20)))
# rs.append(Rect(Vector2(35, 5), Vector2(55, 15)))
#
#
# rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))
# rs.append(Rect(Vector2(8, 8), Vector2(18, 18)))
# rs.append(Rect(Vector2(16, 0), Vector2(26, 10)))
#
# rs.append(Rect(Vector2(10, 28), Vector2(20, 38)))
# rs.append(Rect(Vector2(10, 30), Vector2(20, 40)))
# rs.append(Rect(Vector2(10, 32), Vector2(20, 42)))
# rs.append(Rect(Vector2(0, 35), Vector2(10, 45)))
#
#
# rs.append(Rect(Vector2(0, 0), Vector2(10, 10)))
#
# rs.append(Rect(Vector2(5, 5), Vector2(15, 15)))
#
# rs.append(Rect(Vector2(15, 35), Vector2(25, 45)))
#
# rs.append(Rect(Vector2(60, 0), Vector2(70, 70)))
# rs.append(Rect(Vector2(65, 20), Vector2(75, 30)))
#
#
# rs.append(Rect(Vector2(0, 50), Vector2(10, 60)))
# rs.append(Rect(Vector2(5, 50), Vector2(15, 60)))


def get_events(rects):
    events = {}
    for rect in rects:
        events.setdefault(rect.p1.x, []).append(Event(EventType.BEGIN, rect))
        events.setdefault(rect.p2.x, []).append(Event(EventType.END, rect))
    return events


def get_extents(intervals):
    extents = set()
    for interval in intervals:
        extents.add(interval.begin)
        extents.add(interval.end)
    return extents


g = nx.Graph()


verts = []

tree = IntervalTree()
events = get_events(rs)
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

    # At this point all the vertical edges that lie on T are represented as
    # intervals which do not overlap.

    begins = get_extents(intervals[EventType.BEGIN])
    ends = get_extents(intervals[EventType.END])
    all_ = get_extents(t_tree)

    begin_and_ends = begins.intersection(ends)
    begins -= begin_and_ends
    ends -= begin_and_ends
    all_ |= begin_and_ends

    for vert in begins:
        print 'start:', vert
        open_verts[vert] = t

    for vert in ends:
        print 'end:', vert
        try:
            g.add_edge((open_verts[vert], vert), (t, vert))
            del open_verts[vert]
        except:
            print 'failed to add edge'


    for vert in all_ - begins - ends:
        print 'split:', vert
        g.add_edge((open_verts[vert], vert), (t, vert))
        open_verts[vert] = t

    for i in t_tree:
        g.add_edge((t, i.begin), (t, i.end))
        verts.extend((Vector2(t, i.begin), Vector2(t, i.end)))

    tree.update(IntervalTree(intervals[EventType.BEGIN]))
    tree.difference_update(IntervalTree(intervals[EventType.END]))


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
pos = nx.spring_layout(g)
nx.draw(g, pos=pos)
nx.draw_networkx_labels(g, pos=pos)
plt.show()

