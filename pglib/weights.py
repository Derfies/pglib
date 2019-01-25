import os
import sys
import math

for path in ['uberNode', 'nodeboxapp', 'pglib']:
    sys.path.append( os.path.join( '..', '..', path ) )
from uberNode import UberNode


class SineWeight( UberNode ):

    def __init__( self ):
        super( SineWeight, self ).__init__( inputs=[
            'amplitude',
            'invert',
        ], outputs=[
            'function'
        ] )

        self.inputs['invert'] = False
        self.inputs['amplitude'] = 1

    def evaluate( self ):
        def function( x ):
            value = math.sin( math.radians( x ) )
            if self.inputs['invert']:
                value = 1 - value
            return pow( value, self.inputs['amplitude'] )
        self.outputs['function'] = function


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import numpy as np


    sw = SineWeight()
    xs = range( 45 )
    x = 45
    ys = [math.sin( math.radians( i / (float( x ) - 1) * 180.0 ) ) for i in range( x )]
    plt.plot( xs, ys, 'bo' )
    sw.inputs['invert'] = False
    ys2 = [sw.outputs['function']( i / (float( x ) - 1 ) * 180.0 ) for i in range( x )]
    plt.plot( xs, ys2, 'ro' )
    plt.xlabel( 'x' )
    plt.ylabel( 'y' )
    plt.show()