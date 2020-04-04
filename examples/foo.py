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

        self._points = points

        self.fill = kwargs.get('fill', None)
        self.line = kwargs.get('line', None)
        self.line_width = kwargs.get('line_width', 1)

        self.tris = tripy.earclip(self._points)

        self.batch = pyglet.graphics.Batch()
        for tri in self.tris:
            data = [item for sublist in tri for item in sublist]
            self.batch.add(3, pyglet.gl.GL_TRIANGLES, None, ('v2f', data))

        # Work out line data.
        line_data = []
        for i in range(len(self._points) - 1):
            line_data.extend(self._points[i])
            line_data.extend(self._points[i + 1])
        line_data.extend(self._points[-1])
        line_data.extend(self._points[0])
        self._line_vertex_list = pyglet.graphics.vertex_list(len(line_data) / 2, 'v2f')
        self._line_vertex_list.vertices = line_data

    def draw_fill(self):
        self.batch.draw()

    def draw_line(self):
        self._line_vertex_list.draw(pyglet.gl.GL_LINES)

    def draw(self):
        if self.fill is not None:
            gl.glColor4f(*self.fill)
            self.draw_fill()
        if self.line is not None and self.line_width > 0:
            gl.glLineWidth(self.line_width)
            gl.glColor4f(*self.line)
            self.draw_line()


class Rect(Polygon):

    def __init__(self, p1, p2, **kwargs):
        points = [
            p1,
            Point2d(p1.x, p2.y),
            p2,
            Point2d(p2.x, p1.y),
        ]
        super(Rect, self).__init__(*points, **kwargs)


class Circle(Polygon):

    def __init__(self, centre, radius, num_points, **kwargs):
        self._centre = centre
        self._radius = radius
        self._num_points = num_points

        points = self._get_circle_points()
        super(Circle, self).__init__(*points, **kwargs)

    @property
    def centre(self):
        return self._centre

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius += value

    @property
    def num_points(self):
        return self._num_points

    def _get_circle_points(self):
        points = []
        for i in range(0, self._num_points):
            x = math.cos(2 * math.pi / self._num_points * i) * self._radius
            y = math.sin(2 * math.pi / self._num_points * i) * self._radius
            point = Point2d(x + self._centre.x, y + self._centre.y)
            points.append(point)
        return points


# Run main loop and draw.
window = pyglet.window.Window()
gl.glEnable(pyglet.gl.GL_BLEND)
gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

r = Rect(
    Point2d(30 * GRID_SPACING, 30 * GRID_SPACING), 
    Point2d(40 * GRID_SPACING, 40 * GRID_SPACING),
    fill=(1, 0, 0, 0.5),
    line=(0, 1, 1, 0.5),
    line_width=40
)

# p2 = PointsInCircum(40, 4)
# print len(p2)
# points = map(lambda p: Point2d(*p), p2)
# for point in points:
#     point.x += 100
#     point.y += 100


# p = Polygon(
#     *points,
#     fill=(1,0,0,1),
#     line=(0, 1, 1, 0.5),
#     line_width=10
# )

c = Circle(
    Point2d(30 * GRID_SPACING, 30 * GRID_SPACING), 
    10, 
    10,
    fill=(1,0,0,1)
)


def callback(foo):
    c.radius += 10


pyglet.clock.schedule_interval(callback, 0.5)


@window.event
def on_draw():
    window.clear()

    # r.draw()

    # p.draw()

    c.draw()

    # x = 0
    # y = 0
    # width = 10
    # height = 10

    #batch = pyglet.graphics.Batch()
    #batch.add(3, pyglet.gl.GL_TRIANGLES, None, ('v2i',[10,10,10,50,390,10]))

    # vertex_list = pyglet.graphics.vertex_list(5, 'v2f')#, 'c3B')
    # vertex_list.vertices = [
    #     x, y,
    #     x + width, y,
    #     x + width, y + height,
    #     x, y + height,
    #     x, y + height
    # ]
    #     ('v2f', (
    #         1 * GRID_SPACING, 0 * GRID_SPACING, 
    #         1 * GRID_SPACING, 11 * GRID_SPACING,
    #         11 * GRID_SPACING, 11 * GRID_SPACING,
    #         5 * GRID_SPACING, 5 * GRID_SPACING,
    #         )
    #     ),
    #     #('c3B', (0, 0, 255, 0, 255, 0))
    # )
    #batch.draw()#pyglet.gl.GL_POLYGONS)

pyglet.app.run()