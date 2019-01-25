import random

from region import Region
from uberNode import UberNode


MIN_LEAF_SIZE = 6
MAX_LEAF_SIZE = 20


class BspRegions( UberNode ):

    def __init__( self ):
        UberNode.__init__( self, inputs=[
            'region',
        ], outputs=[
            'regions'
        ] )

    def evaluate( self ):

        """
        Adapted from https://gamedevelopment.tutsplus.com/tutorials/how-to-use-bsp-trees-to-generate-game-maps--gamedev-12268
        """

        leaves = []

        # First, create a leaf to be the 'root' of all leaves.
        root = Region( 
            self.inputs['region'].x1, 
            self.inputs['region'].y1,
            self.inputs['region'].x2, 
            self.inputs['region'].y2
        )
        leaves.append( root )

        # We loop through every leaf in our cector over and over again, until no more leaves can be split.
        didSplit = True
        while didSplit:
            didSplit = False
            for l in leaves:
                if l.leftChild is None and l.rightChild is None: # if this Leaf is not already split...
                
                    # If this Leaf is too big, or 75% chance...
                    if l.width > MAX_LEAF_SIZE or l.height > MAX_LEAF_SIZE or random.uniform( 0, 1 ) > 0.25:
                    
                        if l.split( MIN_LEAF_SIZE ): # split the Leaf!
                        
                            # If we did split, push the child leafs to the Vector so we can loop into them next
                            leaves.append( l.leftChild )
                            leaves.append( l.rightChild )
                            didSplit = True

        self.outputs['regions'] = leaves