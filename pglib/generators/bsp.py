import random

from box import Box
from pglib.const import Axis
from pglib.region import Region


class Bsp(Box):

    def __init__(self, split_dir, **kwargs):
        super(Bsp, self).__init__(**kwargs)

        self.split_dir = split_dir

    def run(self, region):

        # TODO: Want to embed this a little so run automatically gets called
        # with the padding region.
        region = self.get_padding_region(region)

        # TODO: Randomize split amount
        # TODO: Set limits. This is done with the node recursion so far.
        # TODO: Support recursion terminator that still allows the region to
        # be split in the other direction.


        #print '*' * 35
        #print region, 'width:', region.width, 'height:', region.height

        leaves = []
        axis = self.split_dir.run()
        if axis == Axis.X:
            #print 'width:', region.width
            #print 1, region.width - 1
            split = region.x1 + random.randint(1, region.width - 1)
            #print 'split:', split
            leaves.extend([
                Region(region.x1, region.y1, split, region.y2),
                Region(split, region.y1, region.x2, region.y2),
            ])
        else:
            #print 'height:', region.height
            #print 1, region.height - 1
            split = region.y1 + random.randint(1, region.height - 1)
            #print 'split:', split
            leaves.extend([
                Region(region.x1, region.y1, region.x2, split),
                Region(region.x1, split, region.x2, region.y2),
            ])

        #for leave in leaves:
        #    print '->', leave, 'width:', leave.width, 'height:', leave.height

        return leaves