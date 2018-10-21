import random

from region import Region
from uberNode import UberNode


class RandomRegions( UberNode ):

    def __init__( self ):
        UberNode.__init__( self, inputs=[
            'region',
            'minSize',
            'maxSize',
            'maxIterations',
            'intersect',
        ], outputs=[
            'regions'
        ] )

    def evaluate( self ):
        regions = []
        for i in xrange( self.inputs['maxIterations'] ):

            # Create a room with some random dimensions.
            w = random.randint( self.inputs['minSize'], self.inputs['maxSize'] )
            h = random.randint( self.inputs['minSize'], self.inputs['maxSize'] )
            x = random.randint( 0, self.inputs['region'].width - w )
            y = random.randint( 0, self.inputs['region'].height - h )
            region = Region( x, y, x + w, y + h )

            # Check for overlap with previous rooms.
            if self.inputs['intersect']:
                regions.append( region )
            else:
                for otherRegion in regions:
                    if region.intersects( otherRegion ):
                        break
                else:
                    regions.append( region )

        self.outputs['regions'] = regions