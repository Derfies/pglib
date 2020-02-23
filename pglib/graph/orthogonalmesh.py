import networkx as nx

from const import ANGLE, DIRECTION, POSITION, LENGTH, Angle, Direction


class OrthogonalMesh(nx.Graph):

    def can_add_face(self, face):
        dirs_match = []

        directions = {}
        #self.directions = {}
        for idx, edge, direction in face.edge_walk():
            #directions.setdefault(direction, []).append(edge)
            directions[edge] = direction


        for edge in self.get_common_edges(face):
            mesh_dir = self.edges[edge][DIRECTION]
            rev_edge = tuple(reversed(edge))
            face_dir = directions[rev_edge]
            dirs_match.append(face_dir == Direction.opposite(mesh_dir))
        return all(dirs_match)

    def add_face(self, face):
        pos = face.get_node_positions()
        offset = [0, 0]
        common_edges = self.get_common_edges(face)
        if common_edges:
            common_node = common_edges[0][0]
            current = self.nodes[common_node][POSITION]
            incoming = pos[common_node]
            offset = (current[0] - incoming[0], current[1] - incoming[1])

        self.add_edges_from(face)

        # Merge face data into the graph.
        for idx, node in enumerate(face.nodes):
            num_faces = len(self.nodes.get(node, {}).get(ANGLE, {}))
            msg = 'Node {} has {} faces'.format(node, num_faces)
            assert num_faces < 4, msg

            attr = {face: face.angles[idx]}
            self.nodes[node].setdefault(ANGLE, {}).update(attr)
            offset_pos = pos[node]
            offset_pos[0] += offset[0]
            offset_pos[1] += offset[1]
            self.nodes[node][POSITION] = offset_pos


        #def _get_edge_directions(self):
        directions = {}
        #self.directions = {}
        for idx, edge, direction in face.edge_walk():
            #directions.setdefault(direction, []).append(edge)
            directions[edge] = direction
        #return directions

        for edge_idx, edge in enumerate(face):
            attr = directions[edge]
            self.edges[edge][DIRECTION] = attr

        for edge_idx, edge in enumerate(face):
            attr = face.lengths[edge_idx]
            self.edges[edge][LENGTH] = attr

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