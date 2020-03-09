from pglib.region import Region
from base import Base


class Grid(Base):

    def __init__(self, num_rows, num_cols, *args, **kwargs):
        super(Grid, self).__init__(*args, **kwargs)

        self.num_rows = num_rows
        self.num_cols = num_cols

    def generate(self):
        regions = []

        x = self.input_node.data.width / float(self.num_cols)
        y = self.input_node.data.height / float(self.num_rows)

        for i in range(self.num_cols):
            x_offset = self.input_node.data.x1 + i * x
            for j in range(self.num_rows):
                y_offset = self.input_node.data.y1 + j * y
                regions.append(Region(x_offset, y_offset, x_offset + x, y_offset + y))

        return regions