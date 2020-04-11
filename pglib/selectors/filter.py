from base import Base


class Filter(Base):

    def __init__(self, sampler, threshold):
        super(Filter, self).__init__()

        self.sampler = sampler
        self.threshold = threshold

    @property
    def filter(self):
        return filter(lambda x: self.sampler.run() > self.threshold, self.data)