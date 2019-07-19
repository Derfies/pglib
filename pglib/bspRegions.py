import random

from region import Region


def bsp_regions(p_region, min_size, max_size):

    """
    Adapted from https://gamedevelopment.tutsplus.com/tutorials/how-to-use-bsp-trees-to-generate-game-maps--gamedev-12268
    """

    leaves = []

    # First, create a leaf to be the 'root' of all leaves.
    leaves.append(p_region)

    # We loop through every leaf in our cector over and over again, until no more leaves can be split.
    did_split = True
    while did_split:
        did_split = False
        for l in leaves:
            if l.left_child is None and l.right_child is None: # if this Leaf is not already split...
            
                # If this Leaf is too big, or 75% chance...
                if l.width > max_size or l.height > max_size or random.uniform(0, 1) > 0.25:
                
                    if l.split(min_size): # split the Leaf!
                    
                        # If we did split, push the child leafs to the Vector so we can loop into them next
                        leaves.append(l.left_child)
                        leaves.append(l.right_child)
                        did_split = True

    return leaves