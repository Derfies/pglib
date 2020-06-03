import enum
import copy

from pyquaternion import Quaternion
from transformations import (
    translation_matrix,
    translation_from_matrix
)

from pglib.geometry.vector import Vector3
from pglib.geometry.matrix import Matrix4


class Mode(enum.IntEnum):

    REL = 0
    ABS = 1


class CoordSystem(enum.IntEnum):

    PIVOT = 0
    SCOPE = 1
    OBJECT = 2
    WORLD = 3


class AxesSelector(enum.IntEnum):

    X = 0
    Y = 1
    Z = 2
    XY = 3
    XZ = 4
    YZ = 5
    XYZ = 6


class Transform(object):

    def __init__(self, parent=None):
        self.parent = parent

        self.translation = Vector3(0, 0, 0)
        self.rotation = Quaternion(1, 0, 0, 0)
        self.pivot = Vector3(0, 0, 0)

    def __copy__(self):
        tform = self.__class__(self.parent)
        tform.translation = copy.copy(self.translation)
        tform.rotation = copy.copy(self.rotation)
        tform.pivot = copy.copy(self.pivot)
        return tform

    @property
    def matrix(self):
        return Matrix4.compose(self.translation, self.rotation)

    @matrix.setter
    def matrix(self, matrix):
        self.translation = translation_from_matrix(matrix.array)
        self.rotation = Quaternion(matrix=matrix.array)

    @property
    def world_matrix(self):
        if self.parent is None:
            return self.matrix.copy()
        else:
            return self.parent.world_matrix * self.matrix


class Scope(Transform):

    def __init__(self, sx=1, sy=1, sz=1, *args, **kwargs):
        super(Scope, self).__init__(*args, **kwargs)

        self.size = Vector3(sx, sy, sz)

    def __copy__(self):
        scope = super(Scope, self).__copy__()
        scope.size = copy.copy(self.size)
        return scope


class Shape(object):

    def __init__(self, scope):
        self.stack = [copy.copy(scope)]

        # TODO: Figure out better way to treat this stuff.
        self.keep = []
        self.sub_shapes = []

    @property
    def scope(self):
        return self.stack[-1]

    def push(self):
        scope = copy.copy(self.scope)
        self.stack.append(scope)

    def pop(self):
        self.stack.pop()

    def t(self, x, y, z, mode=Mode.REL, coord_system=CoordSystem.SCOPE):
        xyz = Vector3(x, y, z)

        # Rotate the vector to put it into scope space.
        if coord_system == CoordSystem.SCOPE:
            xyz = self.scope.rotation.rotate(xyz)

        if mode == Mode.REL:
            self.scope.translation += xyz
        else:
            self.scope.translation = xyz

    def tx(self, x, mode=Mode.REL, coord_system=CoordSystem.SCOPE):
        self.t(x, 0, 0, mode, coord_system)

    def ty(self, y, mode=Mode.REL, coord_system=CoordSystem.SCOPE):
        self.t(0, y, 0, mode, coord_system)

    def tz(self, z, mode=Mode.REL, coord_system=CoordSystem.SCOPE):
        self.t(0, 0, z, mode, coord_system)

    def r(self, degrees, axis, mode=Mode.REL, coord_system=CoordSystem.SCOPE):

        q = Quaternion(axis=axis, degrees=degrees)

        foo = self.scope.translation + self.scope.rotation.rotate(self.scope.pivot)
        #print 'xformed pivot:', foo

        # This seems off....
        diff = self.scope.translation - foo
        #print 'diff:', diff

        self.scope.rotation *= q

        rot_diff = q.rotate(diff)
        #print 'rot diff:', rot_diff

        self.scope.translation = foo + rot_diff
        #print 'final:', self.scope.translation
        #print ''

        # print 'ROT'
        # print 'trans:', self.scope.translation
        # print 'pivot:', self.scope.pivot

    def rx(self, degrees, mode=Mode.REL, coord_system=CoordSystem.SCOPE):
        self.r(degrees, (1, 0, 0), mode, coord_system)

    def ry(self, degrees, mode=Mode.REL, coord_system=CoordSystem.SCOPE):
        self.r(degrees, (0, 1, 0), mode, coord_system)

    def rz(self, degrees, mode=Mode.REL, coord_system=CoordSystem.SCOPE):
        self.r(degrees, (0, 0, 1), mode, coord_system)

    def s(self, x, y, z, mode=Mode.REL):
        xyz = Vector3(x, y, z)
        if mode == Mode.REL:
            self.scope.size *= xyz
        else:
            self.scope.size = xyz

    def t_pivot(self, x, y, z, mode=Mode.REL, coord_system=CoordSystem.SCOPE):
        xyz = Vector3(x, y, z)
        if mode == Mode.REL:
            self.scope.pivot += xyz
        else:
            self.scope.pivot = xyz

    def center(self, axes_selector=AxesSelector.XYZ, center_pivot=True):

        if len(self.stack) < 2:
            prev = Vector3(0, 0, 0)
        else:
            prev_scope = self.stack[-2]
            prev = prev_scope.translation + prev_scope.rotation.rotate(prev_scope.size / 2.0)
        this = self.scope.translation + self.scope.rotation.rotate(self.scope.size / 2.0)

        diff = prev - this

        if 'x' not in axes_selector.name.lower():
            diff.x = 0
            #print 'skip x'
        if 'y' not in axes_selector.name.lower():
            diff.y = 0
            #print 'skip y'
        if 'z' not in axes_selector.name.lower():
            diff.z = 0
            #print 'skip z'
        self.scope.translation += diff

        # Center the pivot also if required.
        if center_pivot:
            diff = self.scope.size / 2.0

            if 'x' not in axes_selector.name.lower():
                diff.x = 0
                #print 'skip x'
            if 'y' not in axes_selector.name.lower():
                diff.y = 0
                #print 'skip y'
            if 'z' not in axes_selector.name.lower():
                diff.z = 0
                #print 'skip z'

            self.scope.pivot = diff

    def i(self):

        # Kind of a hack to put scopes until I implement something better.
        self.keep.append(copy.copy(self.scope))

    def module(self, cls):
        self.sub_shapes.append(cls(self.scope))


