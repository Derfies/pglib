import abc
import copy

import numpy as np

from pglib.geometry.matrix import Matrix4 as Matrix
from pglib.geometry.point import Point4


class Volume(object):

    """All xform manipulation is done in local space."""

    def __init__(self, x=1, y=1, z=1, matrix=None):
        self.dimensions = Point4(x, y, z)
        self.matrix = matrix if matrix is not None else Matrix()

    @classmethod
    def from_volume(cls, v):
        return cls(
            v.dimensions.x,
            v.dimensions.y,
            v.dimensions.z,
            copy.copy(v.matrix)
        )

    # @classmethod
    # def from_dimensions(cls, d):
    #     return cls(d.x, d.y, d.z)

    def __str__(self):
        str_ = '<Volume x={} y={} z={} matrix=\n{}>'
        return str_.format(
            self.dimensions.x,
            self.dimensions.y,
            self.dimensions.z,
            self.matrix
        )


class Cursor(Volume):

    def __init__(self, *args, **kwargs):
        super(Cursor, self).__init__(*args, **kwargs)

        self.pivot = Point4()


class GeneratorBase(object):

    __metaclass__ = abc.ABCMeta

    class Context(object):

        def __init__(self, generator):
            self.generator = generator

        def __enter__(self):
            v = self.generator.cursor
            self.generator._cursors.append(Volume.from_volume(v))

        def __exit__(self, type, value, traceback):
            self.generator._cursors.pop()

    def __init__(self, volume):
        self.volume = volume
        self._cursors = [Volume.from_volume(volume)]
        self.selectors = {}
        self.run()

    @property
    def cursor(self):
        return self._cursors[-1]

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

    @property
    def x(self):
        return self.cursor.dimensions.x

    @property
    def y(self):
        return self.cursor.dimensions.y

    @property
    def z(self):
        return self.cursor.dimensions.z

    def translate(self, x, y, z):
        self.cursor.matrix.translate((x, y, z))

    def translate_x(self, x):
        self.translate(x, 0, 0)

    def translate_y(self, y):
        self.translate(0, y, 0)

    def translate_z(self, z):
        self.translate(0, 0, z)

    def rotate(self, degrees, axis):
        self.cursor.matrix.rotate(degrees, axis)

    def rotate_x(self, x):
        self.rotate(x, (1, 0, 0))

    def rotate_y(self, y):
        self.rotate(y, (0, 1, 0))

    def rotate_z(self, z):
        self.rotate(z, (0, 0, 1))

    def scale(self, x, y, z):
        self.cursor.dimensions *= Point4(x, y, z, 1)

    def scale_x(self, x):
        self.scale(x, 1, 1)

    def scale_y(self, y):
        self.scale(1, y, 1)

    def scale_z(self, z):
        self.scale(1, 1, z)

    def center(self, arg):
        d = (self.volume.dimensions - self.cursor.dimensions) / 2
        if 'x' in arg:
            self.translate_x(d.x)
        if 'y' in arg:
            self.translate_y(d.y)
        if 'z' in arg:
            self.translate_z(d.z)

    def push(self):
        return self.Context(self)

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

        v.dimensions.x = dimensions[0]
        v.dimensions.y = 0
        v.dimensions.z = dimensions[2]

        v.matrix.translate_x(-dimensions[0] / 2.0)
        v.matrix.translate_y(-dimensions[1] / 2.0)
        v.matrix.translate_z(-dimensions[2] / 2.0)

        rot = Matrix.rotation_matrix(degrees, axis)
        v.matrix = rot * v.matrix

        center = Matrix.translation_matrix((
            self.volume.dimensions.x / 2.0,
            self.volume.dimensions.y / 2.0,
            self.volume.dimensions.z / 2.0
        ))
        v.matrix = self.volume.matrix * center * v.matrix

        return v

    def run(self):
        x, y, z, _ = self.volume.dimensions
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
        height = 5#random.randint(1, 10)
        v.dimensions.z = height
        self.add_selector(v, 'all')

        div_x = DivideX(3, v)
        for div in div_x.select('first', 'last'):
            div_y = DivideY(3, div)
            first, last = div_y.select('first', 'last')

            first.matrix.translate_z(height)
            if first.dimensions.x > 1:
                c = Cantor(first)
                self.add_selectors(c.select('all'), 'all')

            last.matrix.translate_z(height)
            if last.dimensions.x > 1:
                c = Cantor(last)
                self.add_selectors(c.select('all'), 'all')


class CantorRedo(GeneratorBase):

    def run(self):

        height = 5
        self.scale_z(height)

        div_x = self.instantiate(DivideX(3))
        with self.push(div_x.select('first', 'last')):
            div_y = self.instantiate(DivideY(3))
            with self.push(div_y.select('first', 'last')):
                self.instantiate(Branch)



        #for div in DivideX(3, v).select()

        # with self.push():
        #     self.move_z(self.z)
        #     self.rotate_x(15)
        #     self.instantiate(Branch)
        #
        # with self.push():
        #     self.move_z(self.z)
        #     self.rotate_x(-15)
        #     self.instantiate(Branch)


class Branch(GeneratorBase):

    def run(self):

        # Base.

        # Make volume first argument of run?
        v = Volume.from_volume(self.volume)
        v.dimensions *= Point4(0.8, 0.8, 0.9)

        # Make center a function? ie "center this volume"
        center = Matrix.translation_matrix((
            (self.volume.dimensions.x - v.dimensions.x) / 2.0,
            (self.volume.dimensions.y - v.dimensions.y) / 2.0,
            0
        ))
        v.matrix = v.matrix * center
        self.add_selector(v, 'all')


        if self.volume.dimensions[0] > 1:
            for i in range(2):
                b1 = Volume.from_volume(v)
                top = Matrix.translation_matrix((0, 0, v.dimensions[2]))
                rot_x = Matrix.rotation_matrix(15 if i == 0 else -15, (1, 0, 0))
                b1.matrix = b1.matrix * top * rot_x
                c = Branch(b1)
                self.add_selectors(c.select('all'), 'all')


class BranchRedo(GeneratorBase):

    def run(self):

        # Call center first, it moves the cursor...
        self.scale(0.8, 0.8, 0.9)
        self.center('xy')

        print id(self.cursor)
        self.add_selector(self.cursor, 'all')

        with self.push():
            self.translate_z(self.z)
            self.rotate_y(15)

            print id(self.cursor)
            self.add_selector(self.cursor, 'all')

        with self.push():
            self.translate_z(self.z)
            self.rotate_y(-15)

            print id(self.cursor)
            self.add_selector(self.cursor, 'all')