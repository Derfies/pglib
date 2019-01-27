import math
import random

import utils
from region import Region
from uberNode import UberNode


class RandomRegions( UberNode ):

    def __init__( self, inputs=None ):
        if inputs is None:
            inputs = {}
            
        UberNode.__init__( self, inputs=[
            'region',
            'minSize',
            'maxSize',
            'maxIterations',
            'intersect',
            'centerWeight'
        ], outputs=[
            'regions'
        ] )

        self.inputs['centerWeight'] = None

    def evaluate( self ):
        regions = []
        for i in xrange( self.inputs['maxIterations'] ):

            # Randomise some dimensions.
            w = random.randint( self.inputs['minSize'], self.inputs['maxSize'] )
            h = random.randint( self.inputs['minSize'], self.inputs['maxSize'] )

            # Randomise some coords. Weight them towards the center if 
            # specified.
            x, y = 0, 0
            rx = self.inputs['region'].width - w
            ry = self.inputs['region'].height - h
            if self.inputs['centerWeight'] is not None:
                fn = self.inputs['centerWeight'].outputs['function']
                xWeights = {i: fn( i / (float( rx ) - 1 ) * 180.0 ) for i in range( rx )}
                yWeights = {i: fn( i / (float( ry ) - 1 ) * 180.0 ) for i in range( ry )}
                x = utils.weightedChoice( xWeights.items() )
                y = utils.weightedChoice( yWeights.items() )
            else:
                x = random.randint( 0, rx )
                y = random.randint( 0, ry )

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