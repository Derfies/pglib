from pglib.region import Region
from base import Base


class Grid(Base):

    def __init__(self, num_rows, num_cols):
        super(Grid, self).__init__()

        self.num_rows = num_rows
        self.num_cols = num_cols

    def generate(self, region):
        regions = []

        x = region.width / float(self.num_cols)
        y = region.height / float(self.num_rows)

        for i in range(self.num_cols):
            x_offset = region.x1 + i * x
            for j in range(self.num_rows):
                y_offset = region.y1 + j * y
                regions.append(Region(x_offset, y_offset, x_offset + x, y_offset + y))

        return regions