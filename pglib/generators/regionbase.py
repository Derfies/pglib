from pglib.region import Region
from base import Base


class RegionBase(Base):

    def __init__(self, **kwargs):
        super(RegionBase, self).__init__()

        self.padding = kwargs.get('padding')
        self.padding_x1 = kwargs.get('padding_x1')
        self.padding_y1 = kwargs.get('padding_y1')
        self.padding_x2 = kwargs.get('padding_x2')
        self.padding_y2 = kwargs.get('padding_y2')

    def _get_padding_region(self, region):
        x1 = y1 = x2 = y2 = 0
        if self.padding is not None:
            x1 = y1 = x2 = y2 = self.padding.run()
        if self.padding_x1 is not None:
            x1 = self.padding_x1.run()
        if self.padding_y1 is not None:
            y1 = self.padding_y1.run()
        if self.padding_x2 is not None:
            x2 = self.padding_x2.run()
        if self.padding_y2 is not None:
            y2 = self.padding_y2.run()
        return Region(
            region.x1 + x1,
            region.y1 + y1,
            region.x2 - x2,
            region.y2 - y2,
        )

    def run(self, input_):
        padded_region = self._get_padding_region(input_.data)
        return self._run(padded_region)