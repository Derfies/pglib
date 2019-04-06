import random

from region import Region


def bspRegions( pRegion, minSize, maxSize ):

    """
    Adapted from https://gamedevelopment.tutsplus.com/tutorials/how-to-use-bsp-trees-to-generate-game-maps--gamedev-12268
    """

    leaves = []

    # First, create a leaf to be the 'root' of all leaves.
    leaves.append( pRegion )

    # We loop through every leaf in our cector over and over again, until no more leaves can be split.
    didSplit = True
    while didSplit:
        didSplit = False
        for l in leaves:
            if l.leftChild is None and l.rightChild is None: # if this Leaf is not already split...
            
                # If this Leaf is too big, or 75% chance...
                if l.width > maxSize or l.height > maxSize or random.uniform( 0, 1 ) > 0.25:
                
                    if l.split( minSize ): # split the Leaf!
                    
                        # If we did split, push the child leafs to the Vector so we can loop into them next
                        leaves.append( l.leftChild )
                        leaves.append( l.rightChild )
                        didSplit = True

    return leaves