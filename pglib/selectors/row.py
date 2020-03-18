from base import Base


class Row(Base):

    @property
    def left(self):
        return self.data[:1]

    @property
    def middle(self):
        return self.data[1:-1]

    @property
    def right(self):
        return self.data[-1:]