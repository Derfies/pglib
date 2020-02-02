import collections


class Face(collections.MutableSequence):
    
    def __init__(self, edges):
        self.edges = tuple(edges)
        self.nodes = list(set([
            n 
            for edge in self.edges
            for n in edge
        ]))

    def __str__(self):
        return str(self.edges)

    def __len__(self):
        return len(self.edges)

    def __getitem__(self, idx):
        return self.edges[idx]

    def __setitem__(self, idx, edge):
        self.edges[idx] = edge

    def __delitem__(self, idx):
        del self.edges[idx]

    def insert(self, idx, edge):

        # Probably can't do this if the face is enclosed to start with. Only by
        # adding a chord would this work, and that's not really the defintion 
        # I'm after.
        self.edges.insert(idx, edge)

    def reversed(self):
        return Face([tuple(reversed(edge)) for edge in self])