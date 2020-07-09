import networkx as nx


class Face(nx.OrderedDiGraph):

    def __init__(self, *args, **kwargs):
        super(Face, self).__init__(*args, **kwargs)

        # If any node in a directed graph has less than one incident edge
        if any([len(self.edges(node)) < 1 for node in self]):
            raise nx.NetworkXError('Input is not connected.')

        if any([len(self.edges(node)) > 1 for node in self]):
            raise nx.NetworkXError('Input contains a chord.')


class OrthogonalFace(Face):

    pass


if __name__ == '__main__':
    f = Face([('a', 'b'), ('d', 'a'), ('b', 'c'), ('c', 'd')])