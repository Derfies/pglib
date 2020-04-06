import abc
import math

import pyglet
from pyglet import gl

from pglib.geometry.point import Point2d
from pglib.geometry import tripy


GRID_SPACING = 10
WIDTH = 64
HEIGHT = 48
WINDOW_WIDTH = WIDTH * GRID_SPACING
WINDOW_HEIGHT = HEIGHT * GRID_SPACING


class Drawable(object):
    
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def draw(self):
        """"""


class Polygon(Drawable):

    def __init__(self, *points, **kwargs):
        super(Polygon, self).__init__()

        self.points = points
        self.fill = kwargs.get('fill', None)
        self.line = kwargs.get('line', None)
        self.line_width = kwargs.get('line_width', 1)
        self.update()

    def draw_fill(self):
        self._tris.draw()

    def draw_line(self):
        self._verts.draw(pyglet.gl.GL_LINES)

    def draw(self):
        if self.fill is not None:
            gl.glColor4f(*self.fill)
            self.draw_fill()
        if self.line is not None and self.line_width > 0:
            gl.glLineWidth(self.line_width)
            gl.glColor4f(*self.line)
            self.draw_line()

    def update(self):

        # Triangulate ngon and add each triangle to a batch.
        self._tris = pyglet.graphics.Batch()
        for tri in tripy.earclip(self.points):
            v_data = tuple([el for point in tri for el in point])
            self._tris.add(3, pyglet.gl.GL_TRIANGLES, None, ('v2f', v_data))

        # Add all points to a vertex list for the outline.
        line_data = []
        for i in range(len(self.points) - 1):
            line_data.extend(self.points[i])
            line_data.extend(self.points[i + 1])
        line_data.extend(self.points[-1])
        line_data.extend(self.points[0])
        data_len = len(line_data) / 2
        self._verts = pyglet.graphics.vertex_list(data_len, 'v2f')
        self._verts.vertices = line_data


class Rect(Polygon):

    def __init__(self, p1, p2, **kwargs):
        self.p1 = p1
        self.p2 = p2
        super(Rect, self).__init__(**kwargs)

    def _get_rect_points(self):
        return [
            self.p1,
            Point2d(self.p1.x, self.p2.y),
            self.p2,
            Point2d(self.p2.x, self.p1.y),
        ]

    def update(self):
        self.points = self._get_rect_points()
        super(Rect, self).update()


class Circle(Polygon):

    def __init__(self, centre, radius, num_points, **kwargs):
        self.centre = centre
        self.radius = radius
        self.num_points = num_points

        super(Circle, self).__init__(**kwargs)

    def _get_circle_points(self):
        points = []
        for i in range(0, self.num_points):
            x = math.cos(2 * math.pi / self.num_points * i) * self.radius
            y = math.sin(2 * math.pi / self.num_points * i) * self.radius
            point = Point2d(x + self.centre.x, y + self.centre.y)
            points.append(point)
        return points

    def update(self):
        self.points = self._get_circle_points()
        super(Circle, self).update()


# Run main loop and draw.
window = pyglet.window.Window()
gl.glEnable(pyglet.gl.GL_BLEND)
gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

r = Rect(
    Point2d(30 * GRID_SPACING, 30 * GRID_SPACING), 
    Point2d(40 * GRID_SPACING, 40 * GRID_SPACING),
    fill=(1, 1, 0, 0.5),
    line=(0, 1, 1, 0.5),
    line_width=40
)


points = [
    Point2d(10 * GRID_SPACING, 10 * GRID_SPACING), 
    Point2d(10 * GRID_SPACING, 20 * GRID_SPACING), 
    Point2d(20 * GRID_SPACING, 20 * GRID_SPACING), 
    Point2d(15 * GRID_SPACING, 15 * GRID_SPACING), 
    Point2d(20 * GRID_SPACING, 10 * GRID_SPACING), 
]


p = Polygon(
    *points,
    fill=(1, 0.5, 0, 1),
    line=(0, 1, 1, 0.5),
    line_width=10
)

c = Circle(
    Point2d(30 * GRID_SPACING, 30 * GRID_SPACING), 
    100, 
    10,
    fill=(1, 0, 0, 0.5),
    line=(0, 1, 1, 0.5),
    line_width=10
)


def callback(foo):
    print 'update'
    c.radius += 10
    c.num_points += 1
    c.update()

    print r.p2.x
    r.p2.x += 10
    r.update()


#pyglet.clock.schedule_interval(callback, 0.5)


@window.event
def on_draw():
    window.clear()
    r.draw()
    p.draw()
    c.draw()

pyglet.app.run()