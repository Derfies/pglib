import networkx as nx

from pglib.geometry.point import Point2d
from const import ANGLE, DIRECTION, POSITION, LENGTH, Angle, Direction


class OrthogonalMesh(nx.Graph):

    @property
    def node_positions(self):
        return {
            n: pos._data
            for n, pos in nx.get_node_attributes(self, POSITION).items()
        }
    
    # def can_add_face(self, face):
    #     dirs_match = []

    #     directions = {}
    #     #self.directions = {}
    #     for idx, edge, direction in face.edge_walk():
    #         #directions.setdefault(direction, []).append(edge)
    #         directions[edge] = direction


    #     for edge in self.get_common_edges(face):
    #         mesh_dir = self.edges[edge][DIRECTION]
    #         rev_edge = tuple(reversed(edge))
    #         face_dir = directions[rev_edge]
    #         dirs_match.append(face_dir == Direction.opposite(mesh_dir))
    #     return all(dirs_match)

    def add_face(self, face):
        pos = face.get_node_positions()
        offset = Point2d(0, 0)
        common_edges = self.get_common_edges(face)
        if common_edges:
            common_node = common_edges[0][0]
            offset = self.nodes[common_node][POSITION] - pos[common_node]

        self.add_edges_from(face)

        # Merge face data into the graph.
        for idx, node in enumerate(face.nodes):
            num_faces = len(self.nodes.get(node, {}).get(ANGLE, {}))
            msg = 'Node {} has {} faces'.format(node, num_faces)
            assert num_faces < 4, msg
            attr = {face: face.edges[idx].angle}
            self.nodes[node].setdefault(ANGLE, {}).update(attr)
            self.nodes[node][POSITION] = pos[node] + offset

        for edge_idx, edge in enumerate(face):
            self.edges[edge][DIRECTION] = edge.direction
            self.edges[edge][LENGTH] = edge.length

    def get_common_edges(self, face):
        return filter(lambda x: x in self.edges, face.reversed())

    def get_possible_angles(self, node):
        existing_angles = nx.get_node_attributes(self, ANGLE).get(node)
        if existing_angles is None:
            return list(Angle)
        total = sum(existing_angles.values())
        return filter(lambda a: a <= total, Angle)

    # Rename to "get_outer_angle"?
    def get_explementary_angle(self, node):
        existing_angles = nx.get_node_attributes(self, ANGLE).get(node)
        total = sum(map(lambda a: 180 - a, existing_angles.values()))
        return Angle(180 - (360 - total))