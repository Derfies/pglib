import random

import utils
from region import Region


def randomRegions( pRegion, minSize, maxSize, maxIterations, intersect=False, centerWeight=None, **kwargs ):
    regions = []
    for i in xrange( maxIterations ):

        # Randomise some dimensions.
        w = random.randint( minSize, maxSize )
        h = random.randint( minSize, maxSize )

        # Randomise some coords. Weight them towards the center if 
        # specified.
        x, y = 0, 0
        rx = pRegion.width - w
        ry = pRegion.height - h

        if centerWeight is not None:
            xWeights = {i: centerWeight( i / (float( rx ) - 1 ) * 180.0 ) for i in range( rx )}
            yWeights = {i: centerWeight( i / (float( ry ) - 1 ) * 180.0 ) for i in range( ry )}
            x = utils.weightedChoice( xWeights.items() )
            y = utils.weightedChoice( yWeights.items() )
        else:
            x = random.randint( 0, rx )
            y = random.randint( 0, ry )

        # Check for overlap with previous rooms.
        region = Region( x, y, x + w, y + h, **kwargs )
        if intersect:
            regions.append( region )
        else:
            for otherRegion in regions:
                if region.intersects( otherRegion ):
                    break
            else:
                regions.append( region )

    return regions