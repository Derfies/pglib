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

from pglib.geometry.point import Point2d
from pglib.graph.const import ANGLE, DIRECTION, POSITION, LENGTH, Angle, Direction
from pglib.graph.face import Face
from pglib.graph.orthogonalmesh import OrthogonalMesh


GRID_PATH = r'test04.graphml'


class NodeState(enum.IntEnum):

    unknown = 0
    free = 1
    known = 2


class SideState(enum.IntEnum):

    unknown = 0
    known = 2


class Side(object):

    def __init__(self, direction, indices, lengths):
        self.direction = direction

        assert len(indices) == len(lengths), 'Number of indices and lengths must be equal'
        self.indices = tuple(indices)
        self.lengths = tuple(lengths)

    @property
    def state(self):
        state = SideState.known
        if None in self.lengths:
            state = SideState.unknown 
        return state

    @property
    def length(self):
        return sum(self.lengths)

    @property
    def known_length(self):
        return sum([l or 0 for l in self.lengths])

    @property
    def proposed_length(self):
        return sum([l or 1 for l in self.lengths])

    @property
    def num_unknown_edges(self):
        return self.lengths.count(None)


class OrthogonalFace(Face):

    def __init__(self, edges, angles, lengths, direction=Direction.up):
        super(OrthogonalFace, self).__init__(edges)

        assert len(edges) == len(angles) == len(angles), 'Number of edges, angles and lengths must be equal'
        assert sum(angles) == 360, 'Face not closed: {}'.format(angles)

        self.angles = tuple(angles)
        self.lengths = lengths
        self.direction = direction

        self.sides = {}
        for dir_ in Direction:
            indices = []
            lengths = []
            for index in self.get_direction_indices(dir_):
                indices.append(index)
                lengths.append(self.lengths[index])
            self.sides[dir_] = Side(dir_, indices, lengths)

    def edge_walk(self):
        direction = self.direction
        for edge_idx, edge in enumerate(self.edges):
            yield edge_idx, edge, direction
            angle = self.angles[(edge_idx + 1) % len(self.angles)]
            if angle == Angle.inside:
                direction += 1
            elif angle == Angle.outside:
                direction -= 1
            direction = Direction.normalise(direction)

    def get_direction_indices(self, direction):
        return [
            edge_idx
            for edge_idx, edge, edge_dir in self.edge_walk()
            if edge_dir == direction
        ]

    def get_node_positions(self):
        positions = {}
        pos = [0, 0]
        for edge_idx, edge, direction in self.edge_walk():
            positions[edge[0]] = pos[:]
            length = self.lengths[edge_idx]# or 1
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
            self.g.adj[corner], key=lambda node:
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

        faces = []
        smallest_face = sorted(int_faces, key=lambda n: len(n))[0]
        s = [smallest_face]
        while s:
            face = s.pop()
            if face in faces:
                continue
            faces.append(face)

            edge_to_adj_face = {}
            for rev_edge in face.reversed():
                adj_face = edge_to_face.get(rev_edge)
                if adj_face is not None and adj_face not in edge_to_adj_face:
                    edge_to_adj_face[rev_edge] = adj_face
            edge_to_adj_face = sorted(edge_to_adj_face.items(),
                                      key=lambda x: len(x[1]))

            for edge, adj_face in reversed(edge_to_adj_face):
                s.append(adj_face.set_from_edge(edge))

        print ''
        for i, face in enumerate(faces):
            print 'Face:', i, '->', face

        return faces

    def _process_face(self, face_idx, g, indent):

        face = self.faces[face_idx]
        print ''
        print ' ' * indent, 'Process face:', face

        layouts = self.permute_layouts(g, face, indent)
        print ' ' * indent, 'Num layouts:', len(layouts)

        for i, layout in enumerate(layouts):

            # Need to deep copy the graph or else attribute dicts are polluted
            # between copies.
            g_copy = copy.deepcopy(g)
            g_copy.add_face(layout)
          
            # Find adjoining faces.
            if face_idx < len(self.faces) - 1:
                self._process_face(face_idx + 1, g_copy, indent + 4)
            else:
                self.graphs.append(g_copy)

    def _permute_face_angles(self, g, face, indent):

        print ' ' * indent, 'Permute angles:'

        # Warning! These edges aren't guaranteed to be contiguous.
        poss_angles = []
        common_edges = g.get_common_edges(face)
        for node in face.nodes:
            state_idx = len(filter(lambda edge: node in edge, common_edges))
            state = NodeState(state_idx)
            if state == NodeState.known:
                #try:

                angles = []
                try:
                    angles.append(g.get_explementary_angle(node))
                except ValueError:
                    pass
                poss_angles.append(angles)
                # except:

                #     print 'FAILED:', node#, nx.get_node_attributes(g, ANGLE).get(node)
                #     self.debug = g
                #     raise
            elif state == NodeState.unknown:
                poss_angles.append(g.get_possible_angles(node))
            elif state == NodeState.free:
                poss_angles.append(list(Angle))
            print ' ' * (indent + 2), node, state, poss_angles[-1], nx.get_node_attributes(g, ANGLE).get(node)
        all_angle_perms = set(it.product(*poss_angles))
        return filter(lambda x: sum(x) == 360, all_angle_perms)

    def _get_next_walk_direction(self, g, face, indent):

        # Pick an edge-walk direction. If there's a common edge we need to use
        # that same edge's direction in order for the faces to join.
        walk_dir = Direction.up
        rev_edge = tuple(reversed(face[0]))
        if rev_edge in g.edges:
            rev_walk_dir = g.edges[rev_edge][DIRECTION]
            walk_dir = Direction.opposite(rev_walk_dir)
        return walk_dir

    def permute_layouts(self, g, face, indent):

        angle_perms = self._permute_face_angles(g, face, indent + 2)
        walk_dir = self._get_next_walk_direction(g, face, indent + 2)
        
        # Turn each set of 
        ofaces = []
        for angles in angle_perms:

            lengths = [g.edges.get(edge, {}).get(LENGTH) for edge in face]
            oface = OrthogonalFace(face.edges, angles, lengths, walk_dir)
            ofaces.append(oface)

            bar = zip(oface.nodes, oface.angles)
            #print ' ' * (indent + 2), 'Angles:', bar

            missing_lengths = {}
            for dir_, opp_dir in (Direction.xs(), Direction.ys()):

                # Define two sides - one with the shorter proposed length and 
                # one with the longer proposed length.
                min_side, max_side = oface.sides[opp_dir], oface.sides[dir_]
                if max_side.proposed_length < min_side.proposed_length:
                    min_side, max_side = max_side, min_side

                #print ' ' * (indent + 6), 'Axis:', dir_, opp_dir
            
                max_length = max_side.proposed_length

                if min_side.state == SideState.known:
                    max_length = min_side.length
                elif max_side.state == SideState.known:
                    max_length = max_side.length
                #print ' ' * (indent + 8), 'max_length:', max_length

                if min_side.state == SideState.unknown:
                    min_side_edge = (max_length - min_side.known_length) / float(min_side.num_unknown_edges)
                    for edge_idx in min_side.indices:
                        oface.lengths[edge_idx] = oface.lengths[edge_idx] or min_side_edge

                if max_side.state == SideState.unknown:
                    max_side_edge = (max_length - max_side.known_length) / float(max_side.num_unknown_edges)
                    for edge_idx in max_side.indices:
                        oface.lengths[edge_idx] = oface.lengths[edge_idx] or max_side_edge

                #print ' ' * (indent + 8), 'max_side_edge:', [oface.lengths[edge_idx] for edge_idx in max_side.indices]

        return ofaces

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

    #'''
    
    # Create a test graph, pass it to a layouter and run.
    g = create_graph()
    layouter = OrthogonalLayouter(g)
    try:
        layouter.run()
    except:
        if hasattr(layouter, 'debug'):
            init_pyplot((10, 10))
            pos = nx.get_node_attributes(layouter.debug, POSITION)
            nx.draw_networkx(layouter.debug, pos=pos, node_size=200)
            plt.show()
        raise

    # Draw the original graph.
    init_pyplot((30, 5))
    pos = layouter.pos
    for n, p in pos.items():
        p = list(p)
        # p[0] *= 0.01
        # p[1] *= 0.01
        pos[n] = p
    nx.draw_networkx(layouter.g, pos=pos, node_size=200)

    buff = 4
    x_margin = max([p[0] for p in layouter.pos.values()]) + buff
    # y_margin = 0#max([p[1] for p in layouter.pos.values()]) + buff
    print 'TOTAL:', len(layouter.graphs)
    #graph = layouter.debug
    for graph in layouter.graphs[0:5]:
        pos = nx.get_node_attributes(graph, POSITION)
        #print 'pos:', pos

        old_pos = pos.copy()
        for nidx, p in pos.items():
            p[0] += x_margin
            #p[1] += y_margin
        x_margin = max([abs(p[0]) for p in old_pos.values()]) + buff

        nx.draw_networkx(graph, pos)

    plt.show()

    #'''

    '''

    f = Face.from_nodes(range(5))
    angles = [
        Angle.straight,
        Angle.inside,
        Angle.inside,
        Angle.inside,
        Angle.inside,
    ]
    lengths = [
        1,
        1,
        2,
        1,
        1,
    ]



    f = OrthogonalFace(f.edges, angles, lengths)

    for idx, edge, dir_ in f.edge_walk():
        print idx, edge, dir_


    fg = nx.Graph()
    fg.add_edges_from(f)
    nx.draw_networkx(fg, pos=f.get_node_positions())

    plt.show()
    '''


    '''
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
    poss_lengths = [
        5,
        None,
        None,
        None,
        2,
        1,
        None,
        None,
    ]
    f = OrthogonalFace(f.edges, angles, poss_lengths)

    


    # def get_direction_indices(f, dir_):
    #     return [
    #         idx
    #         for idx, edge, direction in f.edge_walk()
    #         if direction == dir_
    #     ]


    # def get_direction_lengths(f, dir_, lengths, default=1):
    #     return [
    #         lengths[idx] or default
    #         for idx in get_direction_indices(f, dir_)
    #     ]


    foobar = {}
    for axis in (Direction.xs(), Direction.ys()):
        print ''
        print '*' * 35
        lengths = {d: sum(f.get_direction_lengths(d)) for d in axis}
        for d, l in lengths.items():
            print d, '->', l

        min_dir = min(lengths, key=lengths.get)
        print 'min_dir:', min_dir

        min_length, max_length = lengths[min_dir], lengths[Direction.opposite(min_dir)]
        print 'min_length:', min_length
        print 'max_length:', max_length

        num_unknowns = f.get_direction_lengths(min_dir, None).count(None)
        print 'num_unknowns:', num_unknowns

        max_perm_length = max_length - sum(f.get_direction_lengths(min_dir, 0)) - (num_unknowns - 1)
        print 'max_perm_length:', max_perm_length

        edge_perms = [
            range(1, max_perm_length + 1) if poss_lengths[idx] is None else [poss_lengths[idx]]
            for idx in f.get_direction_indices(min_dir)
        ]

        for edge_perm in edge_perms:
            print '->', edge_perm

        all_length_perms = it.product(*edge_perms)
        print 'all_length_perms:', filter(lambda x: sum(x) == max_length, all_length_perms)
    '''