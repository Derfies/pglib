from pglib.region import Region
from base import Base


class Box(Base):

    def __init__(self, **kwargs):
        self.padding = kwargs.get('padding')
        self.padding_x1 = kwargs.get('padding_x1')
        self.padding_y1 = kwargs.get('padding_y1')
        self.padding_x2 = kwargs.get('padding_x2')
        self.padding_y2 = kwargs.get('padding_y2')

    def get_padding_region(self, region):
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

    def run(self, region):
        return [self.get_padding_region(region)]