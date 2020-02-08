import enum


ANGLE = 'angle'
DIRECTION = 'direction'
POSITION = 'position'
LENGTH = 'length'


class Angle(enum.IntEnum):

    inside = 90
    outside = -90
    straight = 0


class Direction(enum.IntEnum):

    up = 0
    right = 1
    down = 2
    left = 3

    @staticmethod
    def normalise(direction):
        return Direction(direction % 4)

    @staticmethod
    def opposite(direction):
        return Direction.normalise(direction - 2)

    @staticmethod
    def xs():
        return (Direction.left, Direction.right)

    @staticmethod
    def ys():
        return (Direction.up, Direction.down)