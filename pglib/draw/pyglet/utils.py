import logging
import operator

from pglib import utils
from pglib.geometry.point import Point2d
from pglib.draw.pyglet.drawables import Rect, Image


logger = logging.getLogger(__name__)


def get_drawables(node, grid_spacing):

    regions = []

    def get_outputs(cnode):
        outputs = []
        for input_ in cnode.inputs:
            outputs.extend(input_._recurse_callable(operator.attrgetter('children')))
        return outputs

    for region in node._recurse_callable(get_outputs):
        region = region.data

        if region.width <= 0 or region.height <= 0:
            logger.warning('Skipping region with null area')
            continue

        if hasattr(region, 'image_path'):
            regions.append(Image(
                region.image_path,
                Point2d(region.x1 * grid_spacing, region.y1 * grid_spacing),
                Point2d(region.x2 * grid_spacing, region.y2 * grid_spacing),
                colour=(1, 1, 1, 0.25),
            ))
        if hasattr(region, 'matrix'):
            a = region.matrix
            rows = a.shape[0]
            cols = a.shape[1]
            offset = Point2d(region.x1 * grid_spacing, region.y1 * grid_spacing)
            for x in xrange(rows):
                for y in xrange(cols):
                    if not a[x][y]:
                        continue
                    regions.append(Rect(
                        Point2d(x * grid_spacing, y * grid_spacing) + offset,
                        Point2d((x + 1) * grid_spacing,
                                (y + 1) * grid_spacing) + offset,
                        colour=(1, 0, 0, 1),
                        # line_colour=utils.get_random_colour(1),
                        # line_width=4,
                    ))
        #else:
        regions.append(Rect(
            Point2d(region.x1 * grid_spacing, region.y1 * grid_spacing),
            Point2d(region.x2 * grid_spacing, region.y2 * grid_spacing),
            colour=None,
            line_colour=utils.get_random_colour(1),
            line_width=4,
        ))

    return regions