import os

from pglib.region import Region
from base import Base


class Image(Base):

    def __init__(self, image_path):
        super(Image, self).__init__()

        self.image_path = image_path

    def run(self, region):
        r = Region(region.x1, region.y1, region.x2, region.y2)
        r.image_path = os.path.join('data', self.image_path) + '.png'
        return [r]