from pglib.region import Region
from base import Base


class SingleRegion(Base):

    def __init__(self, colour):
        super(SingleRegion, self).__init__()

        self.colour = colour

    def run(self, region):
        return [Region(region.x1, region.y1, region.x2, region.y2)]