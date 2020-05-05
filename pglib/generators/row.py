from pglib.region import Region
from regionbase import RegionBase


class Row(RegionBase):

    def __init__(self, height, **kwargs):
        super(Row, self).__init__(**kwargs)

        self.height = height

    def _run(self, region):
        regions = []
        height = self.height.run()
        num_cols = region.height / height
        for i in range(num_cols):
            regions.append(Region(
                region.x1, 
                region.y1 + (i * height),
                region.x2, 
                region.y1 + ((i + 1) * height)
            ))
        return regions