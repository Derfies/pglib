import enum


class POS_Y(object):
    numpy_rot = 0
    sign = 1
    dx, dy = 0, 1

class POS_X(object):
    numpy_rot = 1
    sign = 1
    dx, dy = 1, 0

class NEG_Y(object):
    numpy_rot = 2
    sign = -1
    dx, dy = 0, -1

class NEG_X(object):
    numpy_rot = 3
    sign = -1
    dx, dy = -1, 0


POS_Y.opposite = NEG_Y
NEG_Y.opposite = POS_Y
POS_X.opposite = NEG_X
NEG_X.opposite = POS_X


DIRECTIONS = [
    POS_Y,
    POS_X,
    NEG_Y,
    NEG_X,
]


class Direction(enum.IntEnum):

    POS_X = 0
    POS_Y = 1
    NEG_X = 2
    NEG_Y = 3

    @staticmethod
    def normalise(direction):
        return Direction(direction % 4)

    @staticmethod
    def opposite(direction):
        return Direction.normalise(direction - 2)


class Axis(enum.IntEnum):

    X = 0
    Y = 1