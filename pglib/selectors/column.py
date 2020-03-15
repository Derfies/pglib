from base import Base
from pglib.node import Node


class Column(Base):

    @property
    def bottom(self):
        return Node(self.data[:1])

    @property
    def middle(self):
        return Node(self.data[1:-1])

    @property
    def top(self):
        return Node(self.data[-1:])