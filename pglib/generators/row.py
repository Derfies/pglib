from pglib.region import Region
from box import Box


class Row(Box):

    def __init__(self, width, **kwargs):
        super(Row, self).__init__(**kwargs)

        self.width = width
        #self.spacing = spacing

    def run(self, region):

        # TODO: Want to embed this a little so run automatically gets called
        # with the padding region.
        region = self.get_padding_region(region)

        regions = []

        width = self.width.run()
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
            #spacing = self.spacing.run()
        return regions