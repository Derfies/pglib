from pglib.region import Region
from base import Base


class Column(Base):

    def __init__(self, segment_height):
        super(Column, self).__init__()

        self.segment_height = segment_height

    def generate(self, region):
        #print 'region:', region
        regions = []
        num_cols = region.height / self.segment_height
        for i in range(num_cols):
            regions.append(Region(
                region.x1, 
                region.y1 + ((i * self.segment_height)), 
                region.x2, 
                region.y1 + ((i + 1) * self.segment_height)
            ))
            #print '    ->:', regions[-1]
        return regions