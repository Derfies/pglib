from base import Base


class Sequence(Base):

    def first(self, data):
        return data[:1]

    def middle(self, data):
        return data[1:-1]

    def last(self, data):
        return data[-1:]