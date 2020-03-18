from pglib.region import Region
from base import Base


class Row(Base):

    def __init__(self, width_sampler, spacing_sampler):
        super(Row, self).__init__()

        self.width_sampler = width_sampler
        self.spacing_sampler = spacing_sampler

    def run(self, region):
        regions = []
        width = self.width_sampler.run()
        num_rows = region.width / width
        spacing = 0

        # TODO: Spacing may push next element outside of bounds.
        # TODO: Expose this feature?
        for i in range(num_rows):

            # BUG - Set start to end of last region to stop overlapping.
            start = i * (width + spacing)
            regions.append(Region(
                region.x1 + start,
                region.y1,
                region.x1 + start + width,
                region.y2
            ))
            spacing = self.spacing_sampler.run()
        return regions