import networkx as nx


ANGLE = 'angle'


class OrthogonalMesh(nx.Graph):

    def can_add_face(self, face):
        pass

    # def add_face(self, face):
    #     self.add_edges_from(face)

    #     # Merge face data into the graph.
    #     for node in face.nodes:
    #         attr = {face: layout.g.nodes[node][ANGLE]}
    #         self.nodes[node].setdefault(ANGLE, {}).update(attr)

    def get_common_edges(self, face):
        return [
            edge
            for edge in face.reversed()
            if edge in self.edges
        ]