import os
import sys
pkg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
if pkg_path not in sys.path:
    sys.path.append(pkg_path)
import copy
import math
import itertools as it

import enum
import networkx as nx
import matplotlib.pyplot as plt

from pglib.graph.const import ANGLE, DIRECTION, POSITION, Angle, Direction
from pglib.graph.face import Face
from pglib.graph.orthogonalmesh import OrthogonalMesh


GRID_PATH = r'test01.graphml'


class NodeState(enum.IntEnum):

    unknown = 0
    free = 1
    known = 2


class OrthogonalFace(Face):

    def __init__(self, edges, angles, direction=Direction.up):
        super(OrthogonalFace, self).__init__(edges)

        assert len(edges) == len(angles), 'Number of angles not equal to number of edges'
        assert sum(angles) == 360, 'Face not closed: {}'.format(angles)

        self.angles = angles
        self.lengths = {edge: 1 for edge in self}
        self.direction = direction
        self.edge_directions = self._get_edge_directions()

    def get_direction_length(self, direction):
        return sum([
            self.lengths[edge]
            for edge in self.edge_directions[direction]
        ])

    def _get_edge_directions(self):
        directions = {}
        self.directions = {}
        for idx, edge, direction in self.edge_walk():
            directions.setdefault(direction, []).append(edge)
            self.directions[edge] = direction
        return directions

    def edge_walk(self):
        direction = self.direction
        for idx, edge in enumerate(self.edges):
            yield idx, edge, direction
            angle = self.angles[(idx + 1) % len(self.angles)]
            if angle == Angle.inside:
                direction += 1
            elif angle == Angle.outside:
                direction -= 1
            direction = Direction.normalise(direction)

    def get_node_positions(self):
        positions = {}
        pos = [0, 0]
        for idx, edge, direction in self.edge_walk():
            positions[edge[0]] = pos[:]
            length = self.lengths[edge]
            if direction == Direction.up:
                pos[1] += length
            elif direction == Direction.right:
                pos[0] += length
            elif direction == Direction.down:
                pos[1] -= length
            elif direction == Direction.left:
                pos[0] -= length
            else:
                raise Exception('Unknown direction: {}'.format(direction))
        return positions


class OrthogonalLayouter(object):

    def __init__(self, g):
        self._g = g

        self._pos = self.get_planar_layout()
        self._embedding = self.get_planar_embedding()
        self._faces = self.get_inner_faces()

        # Outright fail if any face is less than 4 edges. We can change this to 
        # try to insert new dummy nodes in the future.
        for face in self.faces:
            assert len(face) >= 4, 'Cannot close polygon with less than 4 nodes'

    @property
    def g(self):
        return self._g

    @property
    def pos(self):
        return self._pos

    @property
    def embedding(self):
        return self._embedding

    @property
    def faces(self):
        return self._faces

    def get_planar_layout(self):
        return nx.spectral_layout(self.g)
        return nx.spring_layout(self.g, seed=0)
        return nx.nx_agraph.graphviz_layout(self.g, prog='neato')

    def get_planar_embedding(self):
        """only straight line in G."""
        emd = nx.PlanarEmbedding()
        for node in self.g:
            neigh_pos = {
                neigh: (
                    self.pos[neigh][0] - self.pos[node][0],
                    self.pos[neigh][1] - self.pos[node][1]
                ) for neigh in self.g[node]
            }
            neighes_sorted = sorted(
                self.g.adj[node],
                key=lambda v: math.atan2(
                    neigh_pos[v][1], neigh_pos[v][0])
            )  # counter clockwise
            last = None
            for neigh in neighes_sorted:
                emd.add_half_edge_ccw(node, neigh, last)
                last = neigh
        emd.check_structure()
        return emd

    def get_all_faces(self):
        faces = []
        visited = set()
        for edge in self.embedding.edges():
            if edge in visited:
                continue
            nodes = self.embedding.traverse_face(*edge, mark_half_edges=visited)
            faces.append(Face.from_nodes(nodes))
        return faces

    def get_external_face_half_edge(self):
        corner = min(self.pos, key=lambda n: (self.pos[n][0], self.pos[n][1]))
        other = max(
            g.adj[corner], key=lambda node:
            (self.pos[node][1] - self.pos[corner][1]) /
            math.hypot(
                self.pos[node][0] - self.pos[corner][0],
                self.pos[node][1] - self.pos[corner][1]
            )
        )  # maximum cosine value
        return (other, corner)

    def get_inner_faces(self):
        all_faces = self.get_all_faces()
        ext_hedge = self.get_external_face_half_edge()
        int_faces = filter(lambda x: ext_hedge not in x, all_faces)

        # Build edge -> face dict.
        edge_to_face = {}
        for face in int_faces:
            edge_to_face.update(dict.fromkeys(face, face))


        # for e, fs in edge_to_face.items():
        #     print e, '->', fs

        #for f in set(edge_to_face.values()):
        #    print '->', f

        smallest_face = sorted(int_faces, key=lambda n: len(n))[0]
        s = [smallest_face]
        #done = False


        #for f in int_faces:
        #    print 'f:', f

        i = 0
        faces = []
        while s and i < 10:
            face = s.pop()
            faces.append(face)

            print ''
            print 'face:', face, type(face), face in faces

            #print 'faces:'
            #for f in faces:
            #    print hash(f), type(f), '->', f

            edge_to_adj_face = {
                rev_edge: edge_to_face[rev_edge]
                for rev_edge in face.reversed()
                if rev_edge in edge_to_face and edge_to_face[rev_edge] not in faces
            }
            edge_to_adj_face = sorted(edge_to_adj_face.items(),
                                      key=lambda x: len(x[1]))

            for edge, adj_face in edge_to_adj_face:
                print '    ', edge, '->', adj_face
                s.append(adj_face.set_from_edge(edge))

            #if not s:
            #    done = True

            i += 1

        print ''
        for i, face in enumerate(faces):
            print 'Path:', i, '->', face
        print ''


        # Take the first face and put it on the stack.

        # WHILE

        # take face off stack.

        # process.

        # Gives new faces - put them on stack to process next.

        return faces



    def _process_face(self, face_idx, g, indent):

        # if len(self.graphs) > 0:
        #     return
        
        face = self.faces[face_idx]
        print ' ' * indent, 'Process face:', face

        layouts = self.permute_layouts(g, face, indent)
        print ' ' * indent, 'Num layouts:', len(layouts)
        for i, layout in enumerate(layouts):
            # print ''
            # print ' ' * (indent + 2), 'Eval layout:', i
            # print ' ' * (indent + 2), 'Nodes:', layout.nodes
            # print ' ' * (indent + 2), 'Face:', layout
            # print ' ' * (indent + 2), 'Angles:', layout.angles
            # print ' ' * (indent + 2), 'Directions:'
            # for e in layout:
            #     print ' ' * (indent + 2), e, '->', layout.directions[e]

            can_join = g.can_add_face(layout)
            if not can_join:
                # print ' ' * (indent + 2), '*** CANNOT JOIN ***'
                continue
            # else:
            #     print ' ' * (indent + 2), 'JOINED! Remaining:', len(self.faces) - (face_idx+1)

            # Need to deep copy the graph or else attribute dicts are polluted
            # between copies.
            g_copy = copy.deepcopy(g)
            g_copy.add_face(layout)
          
            # Find adjoining faces.
            if face_idx < len(self.faces) - 1:
                self._process_face(face_idx + 1, g_copy, indent + 4)
            else:
                #print ' ' * (indent + 2), 'FINISHED!'
                self.graphs.append(g_copy)

    def permute_layouts(self, g, face, indent):

        # Warning! These edges aren't guaranteed to be contiguous.
        states = {}
        poss_angles = []
        common_edges = g.get_common_edges(face)
        for node in face.nodes:
            idx = len(filter(lambda edge: node in edge, common_edges))
            node_state = NodeState(idx)
            states[node] = node_state
            if node_state == NodeState.known:
                poss_angles.append([g.get_explementary_angle(node)])
            elif node_state == NodeState.unknown:
                poss_angles.append(g.get_possible_angles(node))
            elif node_state == NodeState.free:
                poss_angles.append(list(Angle))
            else:
                raise Exception('Unknown node state: {}'.format(node_state))
            print ' ' * (indent + 2), node, node_state, poss_angles[-1]

        #nodes, angles = poss_angles.keys(), poss_angles.values() 
        all_angle_perms = set(it.product(*poss_angles))
        angle_perms = filter(lambda x: sum(x) == 360, all_angle_perms)

        #if not angle_perms:
        #    print 'NO PERMS!!'

        #for foo in angle_perms:
        #    print ' ' * (indent + 2), foo

        # Pick an edge-walk direction. If there's a common edge we need to use
        # that same edge's direction in order for the faces to join.
        walk_dir = Direction.up
        if common_edges:
            common_edge = common_edges[0]
            walk_dir = g.edges[common_edge][DIRECTION]
            walk_dir = Direction.opposite(walk_dir)
            #print ' ' * (indent + 2), 'Common edge:', common_edge, walk_dir

            # HAXXOR
            # Need to set the face edge order to go from a common edge.
            # rev_common = tuple(reversed(common_edge))
            # idx = face.index(rev_common)
            # print '\nbefore:', face
            # edges = list(face.edges[idx:])
            # edges.extend(face.edges[:idx])
            # face = Face(edges)
            # print 'after:', face
            # new_angle_perms = []
            # for angles in angle_perms:
            #     angles2 = list(angles[idx:])
            #     angles2.extend(angles[:idx])
            #     new_angle_perms.append(angles2)
            # angle_perms = new_angle_perms

        #print 'walk_dir:', walk_dir

        # Turn each set of 
        layouts = []
        for angles in angle_perms:
            layout = OrthogonalFace(face.edges, angles, walk_dir) 
            layouts.append(layout)


        """Permutes edge lengths"""
        polygons = []

        for layout in layouts:

            foobar = {}
            for axis in (Direction.xs(), Direction.ys()):
                lengths = {d: layout.get_direction_length(d) for d in axis}
                min_dir = min(lengths, key=lengths.get)
                min_length, max_length = lengths[min_dir], lengths[Direction.opposite(min_dir)]
                all_length_perms = it.product(range(1, max_length + 1), repeat=min_length)
                length_perms = filter(lambda x: sum(x) == max_length, all_length_perms)
                foobar[min_dir] = length_perms
                          
            for perm in [dict(zip(foobar, v)) for v in it.product(*foobar.values())]:
                poly = copy.deepcopy(layout)
                for dir_, lengths in perm.items():
                    for i, edge in enumerate(layout.edge_directions[dir_]):
                        poly.lengths[edge] = lengths[i]
                polygons.append(poly)

        return polygons#, all_angle_perms, angle_perms, states, poss_angles

    def run(self):
        self.idx = 0
        self.graphs = []
        self._process_face(0, OrthogonalMesh(), 0)


def init_pyplot(figsize):

    # Set pyplot dimensions.
    plt.figure(figsize=figsize)

    # Then we set up our axes (the plot region, or the area in which we plot things).
    # Usually there is a thin border drawn around the axes, but we turn it off with `frameon=False`.
    ax = plt.axes([0,0,1,1], frameon=False)

    # Then we disable our xaxis and yaxis completely. If we just say 
    # plt.axis('off'), they are still used in the computation of the image 
    # padding.
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # Even though our axes (plot region) are set to cover the whole image with 
    # [0,0,1,1], by default they leave padding between the plotted data and the 
    # frame. We use tigher=True to make sure the data gets scaled to the full 
    # extents of the axes.
    #plt.autoscale(tight=True)
    

def create_graph():
    '''
    g = nx.path_graph(6, create_using=nx.DiGraph)

    # Add an edge from the last to the first node to create an enclosed polygon.
    nodes = list(g.nodes())
    g.add_edge(nodes[-1], nodes[0])

    # 2 squares
    #g.add_edge(nodes[1], nodes[4])

    # 2 squares with single node
    # g.add_edge(nodes[1], '*')
    # g.add_edge('*', nodes[4])

    # 2 squares with two nodes
    # g.add_edge(nodes[1], '1')
    # g.add_edge('1', '2')
    # g.add_edge('2', nodes[4])

    '''
    
    g = nx.Graph(nx.read_graphml(GRID_PATH)).to_directed()
    

    
    #return g.to_directed()
    return nx.Graph(nx.relabel_nodes(g, {
        n: chr(97 + n) for n in range(len(g.nodes()))
    })).to_directed()
    

if __name__ == '__main__':
    f = Face.from_nodes(list(range(8)))
    angles = [
        Angle.straight,
        Angle.straight,
        Angle.inside,
        Angle.inside,
        Angle.straight,
        Angle.straight,
        Angle.inside,
        Angle.inside,
    ]
    f = OrthogonalFace(f.edges, angles)

    poss_lengths = [
        5,
        None,
        None,
        None,
        2,
        None,
        None,
        None,
    ]


    def get_direction_edge_indices(f, dir_):
        return [
            idx
            for idx, edge, direction in f.edge_walk()
            if direction == dir_
        ]


    def get_direction_lengths(f, dir_, lengths, default=1):
        return [
            lengths[idx] or default
            for idx in get_direction_edge_indices(f, dir_)
        ]


    foobar = {}
    for axis in (Direction.xs(), Direction.ys()):
        print ''
        print '*' * 35
        lengths = {d: sum(get_direction_lengths(f, d, poss_lengths)) for d in axis}
        for d, l in lengths.items():
            print d, '->', l

        min_dir = min(lengths, key=lengths.get)
        print 'min_dir:', min_dir

        min_length, max_length = lengths[min_dir], lengths[Direction.opposite(min_dir)]
        print 'min_length:', min_length
        print 'max_length:', max_length

        num_unknowns = get_direction_lengths(f, min_dir, poss_lengths, None).count(None)
        print 'num_unknowns:', num_unknowns

        max_perm_length = max_length - sum(get_direction_lengths(f, min_dir, poss_lengths, 0)) - (num_unknowns - 1)
        print 'max_perm_length:', max_perm_length

        edge_perms = [
            range(1, max_perm_length + 1) if poss_lengths[idx] is None else [poss_lengths[idx]]
            for idx in get_direction_edge_indices(f, min_dir)
        ]

        for edge_perm in edge_perms:
            print '->', edge_perm

        all_length_perms = it.product(*edge_perms)
        print 'all_length_perms:', filter(lambda x: sum(x) == max_length, all_length_perms)