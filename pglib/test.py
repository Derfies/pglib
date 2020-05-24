import abc
import math
import copy
import random
import numpy as np

from transformations import (
    identity_matrix,
    inverse_matrix,
    compose_matrix,
    decompose_matrix,
    concatenate_matrices,
    translation_matrix,
    rotation_matrix,
    scale_matrix,
    scale_from_matrix,
    unit_vector
)


class Matrix(object):

    def __init__(self, array=None):
        self.array = array if array is not None else np.identity(4)

    @classmethod
    def translation_matrix(cls, t):
        m = cls()
        m.translate(t)
        return m

    @classmethod
    def rotation_matrix(cls, angle, axis):
        m = cls()
        m.rotate(angle, axis)
        return m

    @classmethod
    def scale_matrix(cls, s):
        m = cls()
        m.scale(s)
        return m

    def __str__(self):
        return str(self.array)

    def translate(self, t):
        ta = translation_matrix((t[0], t[1], t[2]))
        self.array = concatenate_matrices(self.array, ta)

    def translate_x(self, x):
        self.translate((x, 0, 0))

    def translate_y(self, y):
        self.translate((0, y, 0))

    def translate_z(self, z):
        self.translate((0, 0, z))

    def rotate(self, angle, axis):
        ra = rotation_matrix(math.radians(angle), axis)
        self.array = concatenate_matrices(self.array, ra)

    def rotate_x(self, x):
        self.rotate(x, (1, 0, 0))

    def rotate_y(self, y):
        self.rotate(y, (0, 1, 0))

    def rotate_z(self, z):
        self.rotate(z, (0, 0, 1))

    def scale(self, s):
        sa = np.diag([s[0], s[1], s[2], 1.0])
        self.array = concatenate_matrices(self.array, sa)

    def scale_x(self, x):
        self.scale((x, 1, 1))

    def scale_y(self, y):
        self.scale((1, y, 1))

    def scale_z(self, z):
        self.scale((1, 1, z))

    def __mul__(self, other):
        return self.__class__(concatenate_matrices(self.array, other.array))

    def __copy__(self):
        return self.__class__(self.array.copy())


class Volume(object):

    """All xform manipulation is done in local space."""

    def __init__(self, x=1, y=1, z=1, matrix=None):
        self.dimensions = np.array([x, y, z], dtype=np.float64)
        self.matrix = matrix if matrix is not None else Matrix()

    @classmethod
    def from_volume(cls, v):
        return cls(v.x, v.y, v.z, copy.copy(v.matrix))

    @classmethod
    def from_dimensions(cls, d):
        return cls(d[0], d[1], d[2])

    def __str__(self):
        str_ = '<Volume x={} y={} z={} matrix=\n{}>'
        return str_.format(self.x, self.y, self.z, self.matrix)

    @property
    def x(self):
        return self.dimensions[0]

    @x.setter
    def x(self, x):
        self.dimensions[0] = x

    @property
    def y(self):
        return self.dimensions[1]

    @y.setter
    def y(self, y):
        self.dimensions[1] = y

    @property
    def z(self):
        return self.dimensions[2]

    @z.setter
    def z(self, z):
        self.dimensions[2] = z


class GeneratorBase(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, volume):
        self.volume = volume
        self.selectors = {}
        self.run()

    def add_selector(self, volume, *tags):
        for tag in tags:
            self.selectors.setdefault(tag, []).append(volume)

    def add_selectors(self, volumes, *tags):
        for volume in volumes:
            self.add_selector(volume, *tags)

    def select(self, *tags):
        volumes = []
        for tag in tags:
            volumes.extend(self.selectors[tag])
        return volumes

    @abc.abstractmethod
    def run(self):
        """Generator code goes here."""


class DivideBase(GeneratorBase):

    def __init__(self, index, num_sections, *args, **kwargs):
        self.index = index
        self.num_sections = num_sections
        super(DivideBase, self).__init__(*args, **kwargs)

    def run(self):
        size = self.volume.dimensions[self.index] / float(self.num_sections)
        sections = []
        for i in range(self.num_sections):
            v = Volume.from_volume(self.volume)
            v.dimensions[self.index] = size
            translate = np.zeros(3)
            translate[self.index] = 1
            v.matrix.translate(translate * size * i)
            sections.append(v)

        for section in sections:
            self.add_selector(section, 'all')
        self.add_selector(sections[0], 'first')
        self.add_selector(sections[-1], 'last')
        
        
class DivideX(DivideBase):

    def __init__(self, *args, **kwargs):
        index = 0
        super(DivideX, self).__init__(index, *args, **kwargs)


class DivideY(DivideBase):

    def __init__(self, *args, **kwargs):
        index = 1
        super(DivideY, self).__init__(index, *args, **kwargs)


class DivideZ(DivideBase):

    def __init__(self, *args, **kwargs):
        index = 2
        super(DivideZ, self).__init__(index, *args, **kwargs)


class Box(GeneratorBase):

    def create_face(self, degrees, axis, dimensions):
        v = Volume()
        v.x = dimensions[0]
        v.y = 0
        v.z = dimensions[2]

        v.matrix.translate_x(-dimensions[0] / 2.0)
        v.matrix.translate_y(-dimensions[1] / 2.0)
        v.matrix.translate_z(-dimensions[2] / 2.0)

        rot = Matrix.rotation_matrix(degrees, axis)
        v.matrix = rot * v.matrix

        center = Matrix.translation_matrix((
            self.volume.x / 2.0,
            self.volume.y / 2.0,
            self.volume.z / 2.0
        ))
        v.matrix = self.volume.matrix * center * v.matrix

        return v

    def run(self):
        x, y, z = self.volume.dimensions
        self.add_selector(self.create_face(  0, (0, 0, 1), (x, y, z)), 'all', 'sides', 'x-sides', 'front')
        self.add_selector(self.create_face( 90, (0, 0, 1), (y, x, z)), 'all', 'sides', 'y-sides', 'right')
        self.add_selector(self.create_face(180, (0, 0, 1), (x, y, z)), 'all', 'sides', 'x-sides', 'back')
        self.add_selector(self.create_face(270, (0, 0, 1), (y, x, z)), 'all', 'sides', 'y-sides', 'left')
        self.add_selector(self.create_face(-90, (1, 0, 0), (x, z, y)), 'all',  'ends', 'top')
        self.add_selector(self.create_face( 90, (1, 0, 0), (x, z, y)), 'all',  'ends', 'bottom')


class Columns(GeneratorBase):

    def run(self):

        index = 0

        size = self.volume.dimensions[index] / 3.0
        for i in range(3):
            v = Volume.from_volume(self.volume)
            #v.width = size
            amt = np.array([1, 0, 0]) * i * size
            v.translate(amt)
            self.add_selector(v, 'all')

        #div_x = DivideX(2, self.volume)
        ##for column in div_x.selectors['all']:
        #    self.add_selector(column, 'all')
        # for column in div_x.selectors['all']:
        #     div_y = DivideY(2, column)
        #     for row in div_y.selectors['all']:
        #         div_z = DivideZ(2, row)
        #         for section in div_z.selectors['all']:
        #             self.add_selector(section, 'all')


class Cantor(GeneratorBase):

    def run(self):

        # Base.
        v = Volume.from_volume(self.volume)
        height = random.randint(1, 10)
        v.z = height
        self.add_selector(v, 'all')

        div_x = DivideX(3, v)
        for div in div_x.select('first', 'last'):
            div_y = DivideY(3, div)
            first, last = div_y.select('first', 'last')

            first.matrix.translate_z(height)
            if first.x > 1:
                c = Cantor(first)
                self.add_selectors(c.select('all'), 'all')

            last.matrix.translate_z(height)
            if last.x > 1:
                c = Cantor(last)
                self.add_selectors(c.select('all'), 'all')


class Branch(GeneratorBase):

    def run(self):

        # Base.
        v = Volume.from_volume(self.volume)
        v.x *= 0.8
        v.y *= 0.8
        v.z *= 0.88

        center = Matrix.translation_matrix((
            (self.volume.x - v.x) / 2.0,
            (self.volume.y - v.y) / 2.0,
            0
        ))
        v.matrix = center * v.matrix
        self.add_selector(v, 'all')


        if self.volume.dimensions[0] > 1:
            for i in range(2):
                b1 = Volume.from_volume(v)
                top = Matrix.translation_matrix((0, 0, v.dimensions[2]))
                rot_x = Matrix.rotation_matrix(15 if i == 0 else -15, (1, 0, 0))
                b1.matrix = b1.matrix * top * rot_x
                c = Branch(b1)
                self.add_selectors(c.select('all'), 'all')


if __name__ == '__main__':
    v = Volume(20, 20, 20)
    c = Columns(v)
    c.run()