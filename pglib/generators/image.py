import os

from regionbase import RegionBase


class Image(RegionBase):

    def __init__(self, image_path, **kwargs):
        super(Image, self).__init__(**kwargs)

        self.image_path = image_path

    def _run(self, region):
        region.image_path = os.path.join('data', self.image_path) + '.png'
        return [region]