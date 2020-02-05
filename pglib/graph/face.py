class Face(object):
    
    def __init__(self, edges):
        self.edges = tuple(edges)
        nodes = []
        for edge in self.edges:
            nodes.extend(filter(lambda n: n not in nodes, edge))
        self.nodes = tuple(nodes)

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