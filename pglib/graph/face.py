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
        for edge in self.edges:
            nodes.extend(filter(lambda n: n not in nodes, edge))
        return tuple(nodes)

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