"""
TODO: Differentiate point and vector.
"not all points are vectors, but all vectors are points"
"points can be represented as a vector, but vectors are not points."
Now I'm confused...

https://stackoverflow.com/questions/3913832/what-is-a-3d-vector-and-how-does-it-differ-from-a-3d-point
"""
import numpy as np


class components(object):

    def __init__(self, *components):
        self.components = components

    def __call__(self, cls):
        setattr(cls, '__slots__', self.components)
        for i, component in enumerate(self.components):
            def fget(self, index=i): return self[index]
            def fset(self, value, index=i): self[index] = value
            setattr(cls, component, property(fget, fset))
        return cls


class VectorBase(np.ndarray):

    def __new__(cls, *props):
        if len(props) != len(cls.__slots__):
            msg = '{} takes exactly {} component(s) ({} given)'.format(
                cls.__name__,
                len(cls.__slots__),
                len(props)
            )
            raise ValueError(msg)
        return np.asarray(props, dtype=np.float64).view(cls)

    def __abs__(self):
        return np.linalg.norm(self)

    def dist(self, other):
        return np.linalg.norm(self - other)

    def dot(self, other):
        return np.dot(self, other)


@components('x', 'y')
class Vector2(VectorBase):

    pass


@components('x', 'y', 'z')
class Vector3(VectorBase):

    pass


@components('x', 'y', 'z', 'w')
class Vector4(VectorBase):

    pass