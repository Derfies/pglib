import os

import pyglet

from pglib.region import Region
from base import Base


class Image(Base):

    def __init__(self, image_path):
        super(Image, self).__init__()

        self.image_path = image_path

    def run(self, region):
        sprite_image = pyglet.image.load(
            os.path.join('data', self.image_path) + '.png',
            #min_filter=pyglet.gl.GL_NEAREST
        )
        sprite = pyglet.sprite.Sprite(sprite_image)#, x=50, y=50)
        
        r = Region(region.x1, region.y1, region.x2, region.y2)
        r.sprite_image = sprite_image
        r.sprite = sprite
        return [r]