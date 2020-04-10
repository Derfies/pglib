import abc
import math

import tripy
import pyglet

from pglib.geometry.point import Point2d
from pglib.geometry.rect import Rect as GeoRect
from pglib.geometry.circle import Circle as GeoCircle


class Drawable(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def draw(self):
        """"""


class Line(Drawable):

    def __init__(self, *points, **kwargs):
        super(Line, self).__init__()

        self.points = points
        self.colour = kwargs.get('colour')
        self.width = kwargs.get('width', 1)
        self.update()

    def update(self):
        vertices = []
        for i in range(len(self.points) - 1):
            vertices.extend(self.points[i])
            vertices.extend(self.points[i + 1])
        vertices.extend(self.points[-1])
        vertices.extend(self.points[0])
        len_vertices = len(vertices) / 2
        self._verts = pyglet.graphics.vertex_list(len_vertices, 'v2f')
        self._verts.vertices = vertices

    def draw(self):
        pyglet.gl.glColor4f(*self.colour)
        pyglet.gl.glLineWidth(self.width)
        self._verts.draw(pyglet.gl.GL_LINES)


class Grid(Drawable):

    def __init__(self, width, height, spacing, **kwargs):
        super(Grid, self).__init__()

        self.lines = []
        for x in range(0, width, spacing):
            self.lines.append(Line(Point2d(x, 0), Point2d(x, height), **kwargs))
        for y in range(0, height, spacing):
            self.lines.append(Line(Point2d(0, y), Point2d(width, y), **kwargs))

    def draw(self):
        for line in self.lines:
            line.draw()


class Image(Drawable, GeoRect):

    def __init__(self, path, *args, **kwargs):
        self.path = path
        self.colour = kwargs.get('colour', (1, 1, 1, 1))
        super(Image, self).__init__(*args, **kwargs)
        self.update()

    def draw(self):
        pyglet.gl.glColor4f(*self.colour)
        self.image.blit(*self.p1)

    def update(self):
        self.image = pyglet.image.load(self.path)
        self.image.texture.width = self.width
        self.image.texture.height = self.height


class PolygonBase(Drawable):

    def __init__(self, *args, **kwargs):
        self.colour = kwargs.pop('colour', None)
        self.line_colour = kwargs.pop('line_colour', None)
        self.line_width = kwargs.pop('line_width', 1)
        super(PolygonBase, self).__init__(*args, **kwargs)
        self.update()

    def draw_fill(self):
        self._tris.draw()

    def draw(self):
        if self.colour is not None:
            pyglet.gl.glColor4f(*self.colour)
            self.draw_fill()
        if self.line_colour is not None and self.line_width > 0:
            self.line.draw()

    def update(self):

        # Triangulate ngon and add each triangle to a batch.
        self._tris = pyglet.graphics.Batch()
        for tri in tripy.earclip(self.points):
            v_data = tuple([el for point in tri for el in point])
            self._tris.add(3, pyglet.gl.GL_TRIANGLES, None, ('v2f', v_data))

        self.line = Line(
            *self.points,
            colour=self.line_colour,
            width=self.line_width
        )


class Polygon(PolygonBase):

    def __init__(self, *points, **kwargs):
        self._points = points

        super(Polygon, self).__init__(**kwargs)

    @property
    def points(self):
        return self._points


class Rect(PolygonBase, GeoRect):

    @property
    def points(self):
        return (
            Point2d(self.p1.x, self.p1.y),
            Point2d(self.p1.x, self.p2.y),
            Point2d(self.p2.x, self.p2.y),
            Point2d(self.p2.x, self.p1.y),
        )


class Circle(PolygonBase, GeoCircle):

    def __init__(self, num_points, *args, **kwargs):
        self.num_points = num_points

        super(Circle, self).__init__(*args, **kwargs)

    @property
    def points(self):
        points = []
        for i in range(0, self.num_points):
            x = math.cos(2 * math.pi / self.num_points * i) * self.radius
            y = math.sin(2 * math.pi / self.num_points * i) * self.radius
            point = Point2d(x + self.centre.x, y + self.centre.y)
            points.append(point)
        return points