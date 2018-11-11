import random

import utils
from const import *


class DrunkardsWalk( object ):

    def __init__( self, mapWidth, mapHeight, maxIterations=25000, stepLength=1, weightToPrevDirection=0.7 ):
        self.mapWidth = mapWidth
        self.mapHeight = mapHeight
        self.maxIterations = maxIterations
        self.stepLength = stepLength

        self.level = []
        self.filledGoal = mapWidth * mapHeight * 0.4
        self.weightToCenter = 0.15
        self.weightToPrevDirection = weightToPrevDirection

    def generateLevel( self ):

        # Creates an empty 2D array or clears existing array
        self.level = [
            [1 for y in range( self.mapHeight )]
            for x in range( self.mapWidth )
        ]

        self._numFilled = 0
        self._prevDirection = None

        self.x = random.randint( 2, self.mapWidth - 2 )
        self.y = random.randint( 2, self.mapHeight - 2 )

        for i in xrange( self.maxIterations ):
            self.walk( self.mapWidth, self.mapHeight )
            if self._numFilled >= self.filledGoal:
                break

        return self.level

    def walk( self, mapWidth, mapHeight ):
        dirWeights = dict.fromkeys( [POS_Y, NEG_Y, POS_X, NEG_X], 1.0 )

        # Weight the random walk away from the edges.
        if self.x < mapWidth * 0.25:        # Drunkard is at far left side of map.
            dirWeights[POS_X] += self.weightToCenter
        elif self.x > mapWidth * 0.75:      # Drunkard is at far right side of map.
            dirWeights[NEG_X] += self.weightToCenter
        if self.y < mapHeight * 0.25:       # Drunkard is at the top of the map.
            dirWeights[NEG_Y] += self.weightToCenter
        elif self.y > mapHeight * 0.75:     # Drunkard is at the bottom of the map.
            dirWeights[POS_Y] += self.weightToCenter

        # Weight the random walk in favor of the previous direction.
        if self._prevDirection in dirWeights:
            dirWeights[self._prevDirection] += self.weightToPrevDirection

        # Randomise a direction and a step length.
        direction = utils.weightedChoice( dirWeights.items() )
        stepLength = random.randint( 0, self.stepLength )

        # Mark each cell that makes up the step.
        dx, dy = direction.dx, direction.dy
        for i in range( stepLength ):
            if 0 < self.x + dx < mapWidth - 1 and 0 < self.y + dy < mapHeight - 1:
                self.x += dx
                self.y += dy
                if self.level[self.x][self.y] == 1:
                    self.level[self.x][self.y] = 0
                    self._numFilled += 1
        self._prevDirection = direction