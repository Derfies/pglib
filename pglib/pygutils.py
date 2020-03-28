from functools import partial

import pyglet

from pygprim.context import line, rect
import utils


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


def draw(node, grid_spacing):
    for region in node.outputs:
        if hasattr(region, 'sprite'):
            pyglet.gl.glColor4f(1, 1, 1, 1)
            region.sprite_image.texture.width = region.width * grid_spacing
            region.sprite_image.texture.height = region.height * grid_spacing
            region.sprite_image.blit(region.x1 * grid_spacing, region.y1 * grid_spacing)
        else:
            region_to_rect(
                region, 
                grid_spacing=grid_spacing, 
                stroke=utils.get_random_colour(1),
                strokewidth=4,
                fill=(0, 0, 0, 0)
            )
    for cnode in node.children:
        draw(cnode, grid_spacing)