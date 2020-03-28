import random

from box import Box


class BspRegions(Box):

    def __init__(self, min_size, max_size, **kwargs):
        super(BspRegions, self).__init__(**kwargs)

        self.min_size = min_size
        self.max_size = max_size

    def run(self, region):
        """
        Adapted from https://gamedevelopment.tutsplus.com/tutorials/how-to-use-bsp-trees-to-generate-game-maps--gamedev-12268
        """

        # TODO: Want to embed this a little so run automatically gets called
        # with the padding region.
        region = self.get_padding_region(region)

        leaves = []

        # First, create a leaf to be the 'root' of all leaves.
        leaves.append(region)

        # We loop through every leaf in our cector over and over again, until no more leaves can be split.
        did_split = True
        while did_split:
            did_split = False
            for l in leaves:
                if l.left_child is None and l.right_child is None: # if this Leaf is not already split...
                
                    # If this Leaf is too big, or 75% chance...
                    if l.width > self.max_size or l.height > self.max_size or random.uniform(0, 1) > 0.25:
                    
                        if l.split(self.min_size): # split the Leaf!
                        
                            # If we did split, push the child leafs to the Vector so we can loop into them next
                            leaves.append(l.left_child)
                            leaves.append(l.right_child)
                            did_split = True

        return leaves