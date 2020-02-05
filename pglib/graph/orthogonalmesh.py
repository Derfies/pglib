import networkx as nx

from const import ANGLE, DIRECTION, Angle


class OrthogonalMesh(nx.Graph):

    def __init__(self, *args, **kwargs):
        super(OrthogonalMesh, self).__init__(*args, **kwargs)

        self.faces = []
        self.layouts = []

    def copy(self, *args, **kwargs):
        copy = super(OrthogonalMesh, self).copy(*args, **kwargs)
        copy.faces = self.faces[:]
        copy.layouts = self.layouts[:]
        return copy

    def can_add_face(self, face):
        dirs_match = []
        for edge in self.get_common_edges(face):
            mesh_dir = self.edges[edge][DIRECTION]
            rev_edge = tuple(reversed(edge))
            face_dir = face.directions[rev_edge]
            dirs_match.append(face_dir == mesh_dir)
        return all(dirs_match)

    def add_face(self, face):
        #print '->', type(face)
        self.add_edges_from(face)

        # Merge face data into the graph.
        for node in face.nodes:
            attr = {face: face.angles[node]}
            self.nodes[node].setdefault(ANGLE, {}).update(attr)
        for edge in face:
            attr = face.directions[edge]
            self.edges[edge][DIRECTION] = attr

    def get_common_edges(self, face):
        return filter(lambda x: x in self.edges, face.reversed())

    def get_possible_angles(self, node):
        existing_angles = nx.get_node_attributes(self, ANGLE).get(node)
        if existing_angles is None:
            return list(Angle)
        total = sum(existing_angles.values())
        return filter(lambda a: a <= total, Angle)

    def get_explementary_angle(self, node):
        existing_angles = nx.get_node_attributes(self, ANGLE).get(node)
        total = sum(existing_angles.values())
        return Angle.explementary(total)