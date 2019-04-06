import random

import utils
from const import *


def drunkardsWalk( pRegion, maxIterations=25000, stepLength=1, weightToPrevDirection=0.7 ):

    """
    Stolen with thanks: https://github.com/AtTheMatinee/dungeon-generation
    """

    _numFilled = 0
    _prevDirection = None

    filledGoal = pRegion.width * pRegion.height * 0.4
    weightToCenter = 0.15

    x = random.randint( 2, pRegion.width - 2 )
    y = random.randint( 2, pRegion.height - 2 )

    for i in xrange( maxIterations ):

        dirWeights = dict.fromkeys( [POS_Y, NEG_Y, POS_X, NEG_X], 1.0 )

        # Weight the random walk away from the edges.
        if x < pRegion.width * 0.25:        # Drunkard is at far left side of map.
            dirWeights[POS_X] += weightToCenter
        elif x > pRegion.width * 0.75:      # Drunkard is at far right side of map.
            dirWeights[NEG_X] += weightToCenter
        if y < pRegion.height * 0.25:       # Drunkard is at the top of the map.
            dirWeights[NEG_Y] += weightToCenter
        elif y > pRegion.height * 0.75:     # Drunkard is at the bottom of the map.
            dirWeights[POS_Y] += weightToCenter

        # Weight the random walk in favor of the previous direction.
        if _prevDirection in dirWeights:
            dirWeights[_prevDirection] += weightToPrevDirection

        # Randomise a direction and a step length.
        direction = utils.weightedChoice( dirWeights.items() )
        step = random.randint( 0, stepLength )

        # Mark each cell that makes up the step.
        dx, dy = direction.dx, direction.dy
        for i in range( step ):
            if 0 < x + dx < pRegion.width - 1 and 0 < y + dy < pRegion.height - 1:
                x += dx
                y += dy
                if pRegion.matrix[x][y] == 1:
                    pRegion.matrix[x][y] = 0
                    _numFilled += 1
        _prevDirection = direction

        if _numFilled >= filledGoal:
            break