import random

import utils
from region import Region


def random_regions(p_region, min_size, max_size, max_iters, intersect=False, center_weight=None, **kwargs):
    regions = []
    for i in xrange(max_iters):

        # Randomise some dimensions.
        w = random.randint(min_size, max_size)
        h = random.randint(min_size, max_size)

        # Randomise some coords. Weight them towards the center if 
        # specified.
        x, y = 0, 0
        rx = p_region.width - w
        ry = p_region.height - h

        if center_weight is not None:
            xWeights = {i: center_weight(i / (float(rx) - 1) * 180.0) for i in range(rx)}
            yWeights = {i: center_weight(i / (float(ry) - 1) * 180.0) for i in range(ry)}
            x = utils.get_weighted_choice(xWeights.items())
            y = utils.get_weighted_choice(yWeights.items())
        else:
            x = random.randint(0, rx)
            y = random.randint(0, ry)

        # Check for overlap with previous rooms.
        region = Region(x, y, x + w, y + h, **kwargs)
        if intersect:
            regions.append(region)
        else:
            for other_region in regions:
                if region.intersects(other_region):
                    break
            else:
                regions.append(region)

    return regions