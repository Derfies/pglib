import math
import random

import utils
from region import Region
from uberNode import UberNode


def getSinWeights( x ):
    return {
        i: math.sin( math.radians( i / (float( x ) - 1) * 180.0 ) )
        for i in range( x )
    }


class RandomRegions( UberNode ):

    def __init__( self ):
        UberNode.__init__( self, inputs=[
            'region',
            'minSize',
            'maxSize',
            'maxIterations',
            'intersect',
            'weightToCenter'
        ], outputs=[
            'regions'
        ] )

    def evaluate( self ):
        regions = []
        for i in xrange( self.inputs['maxIterations'] ):

            # Randomise some dimensions.
            w = random.randint( self.inputs['minSize'], self.inputs['maxSize'] )
            h = random.randint( self.inputs['minSize'], self.inputs['maxSize'] )

            # Randomise some coords. Weight them towards the center if 
            # specified.
            x, y = 0, 0
            if self.inputs['weightToCenter']:
                xWeights = getSinWeights( self.inputs['region'].width - w )
                yWeights = getSinWeights( self.inputs['region'].height - h )
                x = utils.weightedChoice( xWeights.items() )
                y = utils.weightedChoice( yWeights.items() )
            else:
                x = random.randint( 0, self.inputs['region'].width - w )
                y = random.randint( 0, self.inputs['region'].height - h )

            # Check for overlap with previous rooms.
            region = Region( x, y, x + w, y + h )
            if self.inputs['intersect']:
                regions.append( region )
            else:
                for otherRegion in regions:
                    if region.intersects( otherRegion ):
                        break
                else:
                    regions.append( region )

        self.outputs['regions'] = regions