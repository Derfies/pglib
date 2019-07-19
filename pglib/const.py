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