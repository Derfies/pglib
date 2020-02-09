class Face(object):
    
    def __init__(self, edges):
        self.edges = tuple(edges)

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
            return set(self.edges) == set(other.edges)
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
        return Face([tuple(reversed(edge)) for edge in self])

    def set_from_edge(self, edge):
        idx = self.index(edge)
        edges = list(self[idx:])
        edges.extend(self[:idx])
        return self.__class__(edges)