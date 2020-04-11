from pglib import utils
from pglib.geometry.point import Point2d
from pglib.draw.pyglet.drawables import Rect, Image


def get_drawables(node, grid_spacing, ret=None):
    ret = ret or []
    for region in node.outputs:
        if hasattr(region, 'image_path'):
            ret.append(Image(
                region.image_path,
                Point2d(region.x1 * grid_spacing, region.y1 * grid_spacing),
                Point2d(region.x2 * grid_spacing, region.y2 * grid_spacing),
            ))
        elif hasattr(region, 'matrix'):
            a = region.matrix
            rows = a.shape[0]
            cols = a.shape[1]
            offset = Point2d(region.x1 * grid_spacing, region.y1 * grid_spacing)
            for x in xrange(rows):
                for y in xrange(cols):
                    if not a[x][y]:
                        continue
                    ret.append(Rect(
                        Point2d(x * grid_spacing, y * grid_spacing) + offset,
                        Point2d((x + 1) * grid_spacing, (y + 1) * grid_spacing) + offset,
                        colour=(1, 0, 0, 1),
                        #line_colour=utils.get_random_colour(1),
                        #line_width=4,
                    ))
        else:
            ret.append(Rect(
                Point2d(region.x1 * grid_spacing, region.y1 * grid_spacing),
                Point2d(region.x2 * grid_spacing, region.y2 * grid_spacing),
                colour=None,
                line_colour=utils.get_random_colour(1),
                line_width=4,
            ))

    for cnode in node.children:
        get_drawables(cnode, grid_spacing, ret)

    return ret