import math

import numpy as np
from transformations import (
    concatenate_matrices,
    translation_matrix,
    rotation_matrix,
    inverse_matrix
)


class Matrix4(object):

    def __init__(self, array=None):
        self.array = array if array is not None else np.identity(4, dtype=np.float64)

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

    def __copy__(self):
        return self.__class__(self.array.copy())

    def __mul__(self, other):
        return self.__class__(concatenate_matrices(self.array, other.array))

    def copy(self):
        return self.__copy__()

    def translate(self, t):
        ta = translation_matrix((t[0], t[1], t[2]))
        self.array = concatenate_matrices(self.array, ta)

    def translate_x(self, x):
        self.translate((x, 0, 0))

    def translate_y(self, y):
        self.translate((0, y, 0))

    def translate_z(self, z):
        self.translate((0, 0, z))

    def rotate(self, angle, axis, origin=None):
        ra = rotation_matrix(math.radians(angle), axis, origin)
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

    def inverse(self):
        return self.__class__(inverse_matrix(self.array))

    @classmethod
    def compose(cls, position, rotation):
        t = cls(translation_matrix(position))
        r = cls(rotation.transformation_matrix)
        return t * r