import networkx as nx


ANGLE = 'angle'


class OrthogonalMesh(nx.Graph):

    def add_face(self, face):
        self.add_edges_from(face)

        # Merge face data into the graph.
        for node in face.nodes:
            attr = {face: layout.g.nodes[node][ANGLE]}
            self.nodes[node].setdefault(ANGLE, {}).update(attr)