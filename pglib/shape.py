import enum
import copy

import numpy as np
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
    def pivot_translation(self):
        #return

        return self.rotation.rotate(self.translation + self.pivot)

    # @property
    # def pivot_matrix(self):
    #     return Matrix4.compose(pivot_translation, self.rotation)

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

    # @world_matrix.setter
    # def world_matrix(self, matrix):
    #     self.matrix = self.parent.world_matrix.inverse() * matrix


class Scope(Transform):

    def __init__(self, *args, **kwargs):
        super(Scope, self).__init__(*args, **kwargs)

        self.size = Vector3(1, 1, 1)

    def __copy__(self):
        scope = super(Scope, self).__copy__()
        scope.size = copy.copy(self.size)
        return scope


# class Pivot(Transform):
#
#     pass


# class Shape(object):
#
#     def __init__(self, parent):
#         self.parent = parent
#
#         self.pivot = Pivot(self.parent)
#         self.scope = Scope(self.pivot)
#
#     def __copy__(self):
#         shape = self.__class__(self.parent)
#         shape.pivot = copy.copy(self.pivot)
#         shape.scope = copy.copy(self.scope)
#         shape.scope.parent = shape.pivot
#         return shape


class Shape(Transform):

    def __init__(self, *args, **kwargs):
        super(Shape, self).__init__(*args, **kwargs)

        self.stack = []
        self.push()

    # @property
    # def shape(self):
    #     return self.stack[-1]
    #
    # @property
    # def pivot(self):
    #     return self.shape.pivot

    @property
    def scope(self):
        return self.stack[-1]

    def push(self):
        if not self.stack:
            scope = Scope(self)
        else:
            scope = copy.copy(self.scope)
        self.stack.append(scope)

    def pop(self):
        self.stack.pop()

    # def insert(self):
    #     pass
    #
    # def center(self):
    #     """
    #     The center operation moves the scope of the current shape to the center
    #     of the previous shape's scope. 'Previous shape' means the previous shape
    #     on the shape stack.
    #
    #     """
    #     if not self.stack or self.stack[-1].parent is None:
    #         print 'bumming out'
    #         return
    #
    #     #shape = self.stack[-1]
    #     prev_shape = self.stack[-2]
    #
    #     #print shape.pivot.world_matrix
    #     #print prev_shape.pivot.world_matrix
    #
    #     scope_world_matrix = self.shape.scope.world_matrix
    #     prev_scope_world_matrix = prev_shape.scope.world_matrix
    #
    #     rel_scope_matrix = prev_scope_world_matrix.inverse() * scope_world_matrix
    #     # print rel_scope_matrix
    #     # shape.scope.matrix = rel_scope_matrix
    #
    #     #self.shape.scope.matrix = self.shape.scope.matrix.inverse() * #prev_shape.pivot.world_matrix.inverse() * rel_scope_matrix
    #     self.shape.scope.matrix = self.shape.pivot.matrix.inverse() * prev_scope_world_matrix
    #
    # def translate(self, mode, coord_system, x, y, z):
    #     """
    #     The translate operation translates the scope. The coordinates can be
    #     defined in any coordinate system, and the translation can either be
    #     absolute (= set to x,y,z) or relative (= add the x,y,z vector). This
    #     operation manipulates the scope position (scope.t attribute).
    #
    #     """
    #     xyz = Vector3(x, y, z)
    #     if mode == Mode.REL:
    #         self.shape.scope.translation += xyz
    #     else:
    #         self.shape.scope.translation = xyz
    #
    # def t(self, tx, ty, tz):
    #     """
    #     The t operation translates the scope by the vector (tx, ty, tz), i.e.
    #     the vector is added to scope.t. If the scope rotation is non-zero, then
    #     the passed translation vector is rotated around the pivot first, with
    #     angles (scope.rx, scope.ry, scope.rz). In other words, the translation
    #     is relative to the scope axes.
    #
    #     The relative operator ' permits a convenient notation relative to the
    #     scope size: t('tx,0,0) is equivalent to t(tx*scope.sx, 0, 0).
    #
    #     Note: t(x,y,z) is the same as translate(rel, scope, x, y, z).
    #
    #     """
    #     self.translate(Mode.REL, CoordSystem.SCOPE, tx, ty, tz)
    #
    # def tx(self, x):
    #     self.t(x, 0, 0)
    #
    # def ty(self, y):
    #     self.t(0, y, 0)
    #
    # def tz(self, z):
    #     self.t(0, 0, z)
    #
    # def rotate(self, mode, coord_system, axis, degrees):
    #     """
    #     The rotate operation rotates the scope around the scope origin. The
    #     angles can be defined in any coordinate system, and the rotation can
    #     either be absolute (= set the angles) or relative (= add the angles).
    #     This operation manipulates the scope orientation with the scope.r
    #     attribute.
    #
    #     """
    #     q = Quaternion(axis=axis, degrees=degrees)
    #     if mode == Mode.REL:
    #         self.shape.pivot.rotation *= q
    #     else:
    #         self.shape.pivot.rotation = q
    #
    # def r(self, axis, degrees):
    #     self.rotate(Mode.REL, CoordSystem.PIVOT, axis, degrees)
    #
    # def rx(self, x):
    #     self.r((1, 0, 0), x)
    #
    # def ry(self, y):
    #     self.r((0, 1, 0), y)
    #
    # def rz(self, z):
    #     self.r((0, 0, 1), z)
    #
    # def s(self, x, y, z, relative=False):
    #     """
    #     Set the size vector of the current shape's scope. If relative is True
    #     then set the size relative to the current shape's scope size:
    #
    #     s(x, 0, 0, relative=True) is equivalent to s(x * scope.scale.x, 0, 0)
    #
    #     """
    #     xyz = Vector3(x, y, z)
    #     if relative:
    #         self.shape.scope.scale *= xyz
    #     else:
    #         self.shape.scope.scale = xyz
    #
    # def sx(self, x, relative=False):
    #     self.s(x, 0, 0, relative)
    #
    # def sy(self, y, relative=False):
    #     self.s(0, y, 0, relative)
    #
    # def sz(self, z, relative=False):
    #     self.s(0, 0, z, relative)

    def t(self, x, y, z, mode=Mode.REL, coord_system=CoordSystem.SCOPE):
        xyz = Vector3(x, y, z)
        if mode == Mode.REL:
            self.scope.translation += xyz
        else:
            self.scope.translation = xyz

    def r(self, degrees, axis, mode=Mode.REL, coord_system=CoordSystem.SCOPE):

        q = Quaternion(axis=axis, degrees=degrees)

        foo = self.scope.translation + self.scope.rotation.rotate(self.scope.pivot)
        print 'xformed pivot:', foo

        # This seems off....
        diff = self.scope.translation - foo
        print 'diff:', diff

        self.scope.rotation *= q

        rot_diff = q.rotate(diff)
        print 'rot diff:', rot_diff

        self.scope.translation = foo + rot_diff
        print 'final:', self.scope.translation
        print ''

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

    def center(self):

        # Get this bb and previous bb.
        


if __name__ == '__main__':

    m = Matrix4()
    m.translate((1,2,3))
    print m.array
    o = Object()
    print o.matrix
    print o.world_matrix
    print o.pivot.matrix
    print o.pivot.world_matrix
    print o.scope.matrix
    print o.scope.world_matrix

    print '*' * 35
    o.translation += (1, 2, 3)

    print o.matrix
    print o.world_matrix
    print o.pivot.matrix
    print o.pivot.world_matrix
    print o.scope.matrix
    print o.scope.world_matrix