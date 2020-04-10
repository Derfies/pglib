import abc
import math

import tripy
import pyglet

from pglib.geometry.point import Point2d
from pglib.geometry.rect import Rect as GeoRect
from pglib.geometry.circle import Circle as GeoCircle


class DrawableBase(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, *args, **kwargs):
        self.colour = kwargs.pop('colour', (1, 1, 1, 1))
        super(DrawableBase, self).__init__(*args, **kwargs)
        self.update()

    @abc.abstractmethod
    def update(self):
        """"""

    @abc.abstractmethod
    def draw_fill(self):
        """"""

    def draw(self):
        if self.colour is not None:
            pyglet.gl.glColor4f(*self.colour)
            self.draw_fill()


class Line(DrawableBase):

    def __init__(self, points, *args, **kwargs):
        self.points = points
        self.width = kwargs.pop('width', 1)
        super(Line, self).__init__(*args, **kwargs)

    def update(self):
        l_data = []
        for i in range(len(self.points) - 1):
            l_data.extend(self.points[i])
            l_data.extend(self.points[i + 1])
        self._verts = pyglet.graphics.vertex_list(len(l_data) / 2, 'v2f')
        self._verts.vertices = l_data

    def draw_fill(self):
        pyglet.gl.glLineWidth(self.width)
        self._verts.draw(pyglet.gl.GL_LINES)


class OutlinedBase(DrawableBase):

    def __init__(self, *args, **kwargs):
        self.line_colour = kwargs.pop('line_colour', None)
        self.line_width = kwargs.pop('line_width', 1)
        super(OutlinedBase, self).__init__(*args, **kwargs)

    @abc.abstractproperty
    def points(self):
        """"""

    def update(self):

        # Triangulate ngon and add each triangle to a batch.
        self._tris = pyglet.graphics.Batch()
        for tri in tripy.earclip(self.points):
            v_data = tuple([el for point in tri for el in point])
            self._tris.add(3, pyglet.gl.GL_TRIANGLES, None, ('v2f', v_data))

        # Use a line object for the outline.
        line_points = list(self.points[:])
        line_points.append(self.points[0])
        self._line = Line(
            line_points,
            colour=self.line_colour,
            width=self.line_width
        )

    def draw_fill(self):
        self._tris.draw()

    def draw_lines(self):
        self._line.draw()

    def draw(self):
        super(OutlinedBase, self).draw()

        if self.line_colour is not None and self.line_width > 0:
            self.draw_lines()


class Polygon(OutlinedBase):

    def __init__(self, points, *args, **kwargs):
        self._points = points
        super(Polygon, self).__init__(*args, **kwargs)

    @property
    def points(self):
        return self._points


class Rect(OutlinedBase, GeoRect):

    @property
    def points(self):
        return (
            Point2d(self.p1.x, self.p1.y),
            Point2d(self.p1.x, self.p2.y),
            Point2d(self.p2.x, self.p2.y),
            Point2d(self.p2.x, self.p1.y),
        )


class Circle(OutlinedBase, GeoCircle):

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

    def draw_fill(self):
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

    def draw_lines(self):
        super(Grid, self).draw_lines()
        for line in self._lines:
            line.draw()