"""
TODO: Differentiate point and vector.
"not all points are vectors, but all vectors are points"

https://stackoverflow.com/questions/3913832/what-is-a-3d-vector-and-how-does-it-differ-from-a-3d-point
"""
import numpy as np


class Vector2(object):

    def __init__(self, x=0, y=0):
        self.array = np.array([x, y], dtype=np.float64)

    def __str__(self):
        return str(self.array)

    def __copy__(self):
        return self.__class__(self.array.copy())

    def __add__(self, other):
        if isinstance(other, Vector4):
            other = other.array
        return self.__class__(*self.array + other)

    def __sub__(self, other):
        if isinstance(other, Vector4):
            other = other.array
        return self.__class__(*self.array - other)

    def __mul__(self, other):
        if isinstance(other, Vector4):
            other = other.array
        return self.__class__(*self.array * other)

    def __div__(self, other):
        if isinstance(other, Vector4):
            other = other.array
        return self.__class__(*self.array / other)

    def __getitem__(self, index):
        return self.array[index]

    def __setitem__(self, index, value):
        self.array[index] = value

    @property
    def x(self):
        return self.array[0]

    @x.setter
    def x(self, x):
        self.array[0] = x

    @property
    def y(self):
        return self.array[1]

    @y.setter
    def y(self, y):
        self.array[1] = y


class Vector3(Vector2):

    """

    """

    def __init__(self, x=0, y=0, z=0):
        self.array = np.array([x, y, z], dtype=np.float64)

    @property
    def z(self):
        return self.array[2]

    @z.setter
    def z(self, z):
        self.array[2] = z


class Vector4(Vector3):

    """

    """

    def __init__(self, x=0, y=0, z=0, w=0):
        self.array = np.array([x, y, z, w], dtype=np.float64)

    @property
    def w(self):
        return self.array[3]

    @w.setter
    def w(self, w):
        self.array[3] = w