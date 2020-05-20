import abc
import random
import numpy as np

from transformations import (
    identity_matrix,
    translation_matrix,
    rotation_matrix,
    scale_matrix,
    concatenate_matrices
)


class Volume(object):

    """All xform manipulation is done in local space."""

    def __init__(self, width=1, height=1, depth=1, xform=None):
        self.width = width
        self.height = height
        self.depth = depth
        self.xform = xform if xform is not None else identity_matrix()

    def __str__(self):
        str_ = '<Volume width={} height={} depth={} xform=\n{}>'
        return str_.format(self.width, self.height, self.depth, self.xform)

    @classmethod
    def from_volume(cls, v):
        return cls(v.width, v.height, v.depth, v.xform.copy())

    def translate(self, value):
        t = translation_matrix(value)
        self.xform = concatenate_matrices(t, self.xform)

    def translate_x(self, value):
        self.translate((value, 0, 0))

    def translate_y(self, value):
        self.translate((0, value, 0))

    def translate_z(self, value):
        self.translate((0, 0, value))

    def rotate(self, value, origin=None):
        origin = origin or (0, 0, 0)
        r = rotation_matrix(value, origin)
        self.xform = concatenate_matrices(r, self.xform)

    def scale(self, factor, direction, origin=None):
        s = scale_matrix(factor, origin=origin, direction=direction)
        self.xform = concatenate_matrices(s, self.xform)

    def scale_x(self, factor, origin=None):
        self.scale(factor, (1, 0, 0), origin)

    def scale_y(self, factor, origin=None):
        self.scale(factor, (0, 1, 0), origin)

    def scale_z(self, factor, origin=None):
        self.scale(factor, (0, 0, 1), origin)


class GeneratorBase(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, volume):
        self.volume = volume
        self.selectors = {}
        self.run()

    def add_selector(self, name, volume):
        self.selectors.setdefault(name, []).append(volume)

    @abc.abstractmethod
    def run(self):
        """Generator code goes here."""


class DivideBase(GeneratorBase):

    def __init__(self, vector, num_sections, *args, **kwargs):
        self.num_sections = num_sections
        self.vector = vector
        super(DivideBase, self).__init__(*args, **kwargs)

    def run(self):
        size = 1 / float(self.num_sections)
        for i in range(self.num_sections):
            v = Volume.from_volume(self.volume)
            v.scale(size, self.vector)
            v.translate(self.vector * size * i)
            self.add_selector('all', v)
        
        
class DivideX(DivideBase):

    def __init__(self, *args, **kwargs):
        vector = np.array([1, 0, 0])
        super(DivideX, self).__init__(vector, *args, **kwargs)


class DivideY(DivideBase):

    def __init__(self, *args, **kwargs):
        vector = np.array([0, 1, 0])
        super(DivideY, self).__init__(vector, *args, **kwargs)


class DivideZ(DivideBase):

    def __init__(self, *args, **kwargs):
        vector = np.array([0, 0, 1])
        super(DivideZ, self).__init__(vector, *args, **kwargs)


class Columns(GeneratorBase):

    def run(self):
        div_x = DivideX(10, self.volume)
        for column in div_x.selectors['all']:
            div_z = DivideZ(4, column)
            for section in div_z.selectors['all']:
                self.add_selector('all', section)


if __name__ == '__main__':
    v = Volume(20, 20, 20)
    c = Columns(v)
    c.run()