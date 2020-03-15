from base import Base
from pglib.node import Node


class Column(Base):

    def select(self, data):
        return [Node(data)]