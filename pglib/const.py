class POS_Y( object ):
    numpyRot = 0
    sign = 1
    dx, dy = 0, 1

class POS_X( object ):
    numpyRot = 1
    sign = 1
    dx, dy = 1, 0

class NEG_Y( object ):
    numpyRot = 2
    sign = -1
    dx, dy = 0, -1

class NEG_X( object ):
    numpyRot = 3
    sign = -1
    dx, dy = -1, 0


DIRECTIONS = [
    POS_Y,
    POS_X,
    NEG_Y,
    NEG_X,
]