import networkx as nx

from const import Direction, DIRECTION, ANGLE


class OrthogonalMesh(nx.Graph):

    def can_add_face(self, face):
        dirs_match = []
        for edge in self.get_common_edges(face):
            mesh_dir = self.edges[edge][DIRECTION]
            rev_edge = tuple(reversed(edge))
            face_dir = face.directions[rev_edge]
            rev_face_dir = Direction.opposite(face_dir)
            dirs_match.append(rev_face_dir == mesh_dir)
        return all(dirs_match)

    def add_face(self, face):
        self.add_edges_from(face)

        # Merge face data into the graph.
        for node in face.nodes:
            attr = {face: face.angles[node]}
            self.nodes[node].setdefault(ANGLE, {}).update(attr)
        for edge in face:
            attr = face.directions[edge]
            self.edges[edge][DIRECTION] = attr

    def get_common_edges(self, face):
        return [
            edge
            for edge in face.reversed()
            if edge in self.edges
        ]