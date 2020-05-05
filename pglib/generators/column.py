from pglib.region import Region
from regionbase import RegionBase


class Column(RegionBase):

    def __init__(self, width, **kwargs):
        super(Column, self).__init__(**kwargs)

        self.width = width

    def _run(self, region):
        regions = []
        width = self.width.run()
        num_rows = region.width / width
        for i in range(num_rows):
            regions.append(Region(
                region.x1 + (i * width),
                region.y1,
                region.x1 + ((i + 1) * width),
                region.y2
            ))
        return regions