from collections import Sequence


class Edge(Sequence):
    
    def __init__(self, nodes):
        self._nodes = tuple(nodes)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._nodes == other._nodes
        return self._nodes == other

    def __str__(self):
        return str(self._nodes)

    def __len__(self):
        return len(self._nodes)

    def __hash__(self):
        return hash(self._nodes)  

    def __getitem__(self, index):
        return self._nodes[index]

    def reversed(self):
        return self.__class__(reversed(self._nodes))


class Face(object):

    edge_class = Edge
    
    def __init__(self, *args):
        self.edges = tuple([self.edge_class(*args) for args in zip(*args)])

    @classmethod
    def from_nodes(cls, nodes):
        return cls([
            (nodes[idx], nodes[(idx + 1) % len(nodes)])
            for idx in range(len(nodes))
        ])

    @property
    def nodes(self):
        nodes = []
        for edge in self:
            nodes.extend(filter(lambda n: n not in nodes, edge))
        return tuple(nodes)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return set(self) == set(other)
        return False

    def __str__(self):
        return str(self.edges)

    def __len__(self):
        return len(self.edges)

    def __getitem__(self, idx):
        return self.edges[idx]

    def index(self, edge):
        return self.edges.index(edge)

    def reversed(self):
        return Face(map(self.edge_class.reversed, self))

    def set_from_edge(self, edge):
        idx = self.index(edge)
        edges = list(self[idx:])
        edges.extend(self[:idx])
        return self.__class__(edges)