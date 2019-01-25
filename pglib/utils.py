import bisect
import random

from const import *


def getRandomColour( a=0.25 ):
    r = random.uniform( 0.0, 1.0 )
    g = random.uniform( 0.0, 1.0 )
    b = random.uniform( 0.0, 1.0 )
    return r, g, b, a


def getRandomDirection( directions=None ):
    directions = directions or DIRECTIONS
    idx = random.randint( 0, len( directions ) - 1 )
    return directions[idx]


def weightedChoice( choices ):
    values, weights = zip( *choices )
    total = 0
    cumWeights = []
    for weight in weights:
        total += weight
        cumWeights.append( total )
    x = random.random() * total
    i = bisect.bisect( cumWeights, x )
    return values[i]