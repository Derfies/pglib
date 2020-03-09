from functools import partial

from pygprim.context import line, rect


def grid(width, height, spacing, stroke):
    for x in range(0, width, spacing):
        line(x, 0, x, height, stroke=stroke)
    for y in range(0, height, spacing):
        line(0, y, width, y, stroke=stroke)


def region_to_rect(region, **kwargs):
    grid_spacing = kwargs.pop('grid_spacing', 1)
    x = region.x1 * grid_spacing
    y = region.y1 * grid_spacing
    w = region.width * grid_spacing
    h = region.height * grid_spacing
    rect(x, y, w, h, **kwargs)