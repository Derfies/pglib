import abc
import math

import tripy
import pyglet

from pglib.geometry.point import Point2d
from pglib.geometry.rect import Rect as GeoRect
from pglib.geometry.circle import Circle as GeoCircle


class Drawable(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        self.colour = kwargs.pop('colour', (1, 1, 1, 1))
        super(Drawable, self).__init__(*args, **kwargs)
        self.update()

    @abc.abstractmethod
    def update(self):
        """"""

    @abc.abstractmethod
    def _draw(self):
        """"""

    def draw(self):
        if self.colour is not None:
            pyglet.gl.glColor4f(*self.colour)
            self._draw()


class Line(Drawable):

    def __init__(self, points, *args, **kwargs):
        self.points = points
        self.width = kwargs.pop('width', 1)
        super(Line, self).__init__(*args, **kwargs)

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

    def _draw(self):
        pyglet.gl.glLineWidth(self.width)
        self._verts.draw(pyglet.gl.GL_LINES)


class PolygonBase(Drawable):

    def __init__(self, *args, **kwargs):
        self.line_colour = kwargs.pop('line_colour', None)
        self.line_width = kwargs.pop('line_width', 1)
        super(PolygonBase, self).__init__(*args, **kwargs)

    @abc.abstractproperty
    def points(self):
        """"""

    def update(self):

        # Triangulate ngon and add each triangle to a batch.
        self._tris = pyglet.graphics.Batch()
        for tri in tripy.earclip(self.points):
            v_data = tuple([el for point in tri for el in point])
            self._tris.add(3, pyglet.gl.GL_TRIANGLES, None, ('v2f', v_data))

        self._line = Line(
            self.points,
            colour=self.line_colour,
            width=self.line_width
        )

    def _draw(self):
        self._tris.draw()

    def draw(self):
        super(PolygonBase, self).draw()

        if self.line_colour is not None and self.line_width > 0:
            self._line.draw()


class Polygon(PolygonBase):

    def __init__(self, points, *args, **kwargs):
        self._points = points
        super(Polygon, self).__init__(*args, **kwargs)

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


class Image(Rect):

    def __init__(self, path, *args, **kwargs):
        self.path = path
        super(Image, self).__init__(*args, **kwargs)

    def update(self):
        super(Image, self).update()
        self._image = pyglet.image.load(self.path)
        self._image.texture.width = self.width
        self._image.texture.height = self.height

    def _draw(self):
        super(Image, self)._draw()
        self._image.blit(*self.p1)


class Grid(Rect):

    def __init__(self, spacing, *args, **kwargs):
        self.spacing = spacing
        super(Grid, self).__init__(*args, **kwargs)

    def update(self):
        super(Grid, self).update()
        self._lines = []
        kwargs = {'colour': self.line_colour}
        for x in range(self.p1.x, self.p2.x, self.spacing):
            line = Line((Point2d(x, self.p1.y), Point2d(x, self.p2.y)), **kwargs)
            self._lines.append(line)
        for y in range(self.p1.y, self.p2.y, self.spacing):
            line = Line((Point2d(self.p1.x, y), Point2d(self.p2.x, y)), **kwargs)
            self._lines.append(line)

    def draw(self):
        super(Grid, self).draw()
        for line in self._lines:
            line.draw()