from pglib.region import Region
from base import Base


class SingleRegion(Base):

    def generate(self):
        r = self.input_node.data
        return [Region(r.x1, r.y1, r.x2, r.y2)]