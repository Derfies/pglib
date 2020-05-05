from pglib.region import Region
from regionbase import RegionBase


class Grid(RegionBase):

    def __init__(self, num_rows, num_cols, **kwargs):
        super(Grid, self).__init__(**kwargs)

        self.num_rows = num_rows
        self.num_cols = num_cols

    def _run(self, region):
        regions = []

        num_cols = self.num_cols.run()
        num_rows = self.num_rows.run()

        x = region.width / float(num_cols)
        y = region.height / float(num_rows)

        for i in range(num_cols):
            x_offset = region.x1 + i * x
            for j in range(num_rows):
                y_offset = region.y1 + j * y
                regions.append(Region(x_offset, y_offset, x_offset + x, y_offset + y))

        return regions