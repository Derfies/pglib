from base import Base


class Column(Base):

    @property
    def bottom(self):
        return self.data[:1]

    @property
    def middle(self):
        return self.data[1:-1]

    @property
    def top(self):
        return self.data[-1:]