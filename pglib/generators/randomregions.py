import random

from pglib import utils
from pglib.region import Region
from base import Base


class RandomRegions(Base):

    def __init__(self, width_sampler, height_sampler, max_iters, intersect=False,
                 center_weight=None):
        self.width_sampler = width_sampler
        self.height_sampler = height_sampler
        self.max_iters = max_iters
        self.intersect = intersect
        self.center_weight = center_weight

    def run(self, p_region):
        regions = []
        for i in xrange(self.max_iters):

            # Randomise some dimensions.
            #w = random.randint(self.min_size, self.max_size)
            #h = random.randint(self.min_size, self.max_size)
            w = self.width_sampler.run()
            h = self.height_sampler.run()

            # Randomise some coords. Weight them towards the center if
            # specified.
            x, y = 0, 0
            rx = p_region.width - w
            ry = p_region.height - h

            if self.center_weight is not None:
                xWeights = {i: center_weight(i / (float(rx) - 1) * 180.0) for i
                            in range(rx)}
                yWeights = {i: center_weight(i / (float(ry) - 1) * 180.0) for i
                            in range(ry)}
                x = utils.get_weighted_choice(xWeights.items())
                y = utils.get_weighted_choice(yWeights.items())
            else:
                x = random.randint(0, rx)
                y = random.randint(0, ry)

            # Check for overlap with previous rooms.
            region = Region(x, y, x + w, y + h)
            if self.intersect:
                regions.append(region)
            else:
                for other_region in regions:
                    if region.intersects(other_region):
                        break
                else:
                    regions.append(region)

        return regions