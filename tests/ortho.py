import os
import sys
if os.path.dirname(__file__) not in sys.path:
    sys.path.append(os.path.dirname(__file__))
import copy
import math
import itertools as it

import enum
import networkx as nx
import matplotlib.pyplot as plt

from pglib.graph import const
from pglib.graph.face import Face
from pglib.graph.orthogonalmesh import OrthogonalMesh


NUM_NODES = 6
LENGTH = 'length'
ANGLE = 'angle'
POSITION = 'position'
DIRECTION = 'direction'
GRID_PATH = r'test01.graphml'


class Angle(enum.IntEnum):

    inside = 90
    outside = -90
    straight = 0


class OrthogonalFace(Face):

    def __init__(self, face, angles):
        super(OrthogonalFace, self).__init__(face)

        self.angles = {
            node: angles[(idx + 1) % len(self)]
            for idx, node in enumerate(self.nodes)
        }
        self.lengths = {edge: 1 for edge in self}

        self.edges = face   # Edges are ordered at this point.
        self.edge_directions = self._get_edge_directions()

    def get_direction_length(self, direction):
        return sum([
            self.lengths[edge]
            for edge in self.edge_directions[direction]
        ])
    
    @property
    def width(self):
        return max(map(self.get_direction_length, Direction.xs()))

    @property
    def height(self):
        return max(map(self.get_direction_length, Direction.ys()))

    def _get_edge_directions(self):
        directions = {}
        self.directions = {}
        for edge, direction in list(self.edge_walk(const.Direction.up)):
            #self.g[edge[0]][edge[1]][DIRECTION] = direction
            directions.setdefault(direction, []).append(edge)
            #self.g.edges[edge][DIRECTION] = direction
            self.directions[edge] = direction
        return directions

    def edge_walk(self, direction):
        for edge in self.edges:
            yield edge, direction
            angle = self.angles[edge[1]]#self.g.node[edge[1]][ANGLE]   # WRONG ANGLE BEING ENCODED
            if angle == Angle.inside:
                direction += 1
            elif angle == Angle.outside:
                direction -= 1
            direction = const.Direction.normalise(direction)

    def vertex_positions(self):
        positions = {}
        pos = [0, 0]
        for edge, direction in list(self.edge_walk(const.Direction.up)):
            positions[edge[0]] = pos[:]
            length = self.lengths[edge]#self.g.edges[edge][LENGTH]
            if direction == const.Direction.up:
                pos[1] += length
            elif direction == const.Direction.right:
                pos[0] += length
            elif direction == const.Direction.down:
                pos[1] -= length
            else:   # Direction.left
                pos[0] -= length
        return positions


class OrthogonalLayouter(object):

    def __init__(self, g):
        self._g = g

        self._pos = self.get_planar_layout()
        self._embedding = self.get_planar_embedding()
        self._faces = self.get_faces()

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
        return nx.spring_layout(self.g, seed=0)

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
            edges = [
                (nodes[idx], nodes[(idx + 1) % len(nodes)])
                for idx in range(len(nodes))
            ]
            faces.append(Face(edges))
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

    def get_faces(self):
        faces = self.get_all_faces()
        ext_hedge = self.get_external_face_half_edge()
        int_faces = filter(lambda x: ext_hedge not in x, faces)
        return sorted(int_faces, key=lambda x: len(x))

    def _process_face(self, face, g):
        print '\n->', face

        # Find the edges that are common to both the face and the rest of the 
        # graph.
        common = g.get_common_edges(face)
        #print 'common edges:', common

        # Turn these into contiguous sets. (?)

        # Find the directions of these edges.

        dirs = {
            edge: g.edges[edge][DIRECTION]
            for edge in common
        }
        print 'common edge dirs:', dirs

        # Permute layouts or filter layouts using these angles.

        self.done_faces.append(face)

        face_added = False
        for poly in self.permute_layouts(face)[0:1]:

            # Test for poly validity here?
            g_copy = g.copy()
            #g_copy.add_edges_from(poly.edges)
            

            can_join = g.can_add_face(poly)
            print 'CAN JOIN:', can_join
            if not can_join:
                continue
            g_copy.add_face(poly)
            self.polys.append(poly)
          
            # Find adjoining faces.
            adj_faces = []
            for adj_face in layouter.faces:
                rev_face = adj_face.reversed()
                if adj_face not in self.done_faces and (set(face) & set(rev_face)):
                    self._process_face(adj_face, g_copy)

    def run(self):
        self.done_faces = []
        self.polys = []
        self._process_face(self.faces[0], OrthogonalMesh())


    def permute_layouts(self, face):

        # We need four inside corners in order to close the polygon.
        num_nodes = len(face)
        num_spare_nodes = num_nodes - 4

        # Calculate all possible combinations of spare angles. Filter out all
        # combinations that do not add up to zero, as these will leave the polygon
        # unclosed.
        all_spare_angle_perms = it.product(Angle, repeat=num_spare_nodes)
        spare_angle_perms = filter(lambda x: sum(x) == 0, all_spare_angle_perms)

        # Calculate all possible positions of the minimum four required inside
        # corners.
        inside_angle_perms = [
            tuple([
                Angle.inside if idx not in idxs else None # Do we need to do outside corner?
                for idx in range(num_nodes)
            ])
            for idxs in it.combinations(range(num_nodes), num_spare_nodes)
        ]

        # Create all combinations using the above.
        angle_perms = []
        for spare_angles in spare_angle_perms:
            for inside_angles in inside_angle_perms:
                spare_angles_iter = iter(spare_angles)
                angle_perms.append(tuple([
                    inside_angle or spare_angles_iter.next()
                    for inside_angle in inside_angles
                ]))

        print 'total num layouts:', len(angle_perms)
        print 'unique num layouts:', len(set(angle_perms))
        layouts = [OrthogonalFace(face, angles) for angles in set(angle_perms)]
        if len(layouts) == 21:
            layouts = layouts[10:11]
        #return layouts


        # TO DO: CLEAN THIS UP


        #def permute_polygons(self):
        """Permutes edge lengths"""
        polygons = []

        for layout in layouts:

            foobar = {}
            for axis in (const.Direction.xs(), const.Direction.ys()):
                lengths = {d: layout.get_direction_length(d) for d in axis}
                min_dir = min(lengths, key=lengths.get)
                min_length, max_length = lengths[min_dir], lengths[const.Direction.opposite(min_dir)]
                all_length_perms = it.product(range(1, max_length + 1), repeat=min_length)
                length_perms = filter(lambda x: sum(x) == max_length, all_length_perms)
                foobar[min_dir] = length_perms
                          
            for perm in [dict(zip(foobar, v)) for v in it.product(*foobar.values())]:
                poly = copy.deepcopy(layout)
                for dir_, lengths in perm.items():
                    for i, edge in enumerate(layout.edge_directions[dir_]):
                        poly.lengths[edge] = lengths[i]
                polygons.append(poly)

        return polygons


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
    plt.autoscale(tight=True)
    

def create_graph():
    '''
    g = nx.path_graph(NUM_NODES, create_using=nx.DiGraph)

    # Add an edge from the last to the first node to create an enclosed polygon.
    nodes = list(g.nodes())
    g.add_edge(nodes[-1], nodes[0])
    g.add_edge(nodes[1], nodes[4])
    '''

    g = nx.Graph(nx.read_graphml(GRID_PATH)).to_directed()

    return nx.Graph(nx.relabel_nodes(g, {
        n: chr(97 + n) for n in range(len(g.nodes()))
    })).to_directed()


# Create a test graph, pass it to a layouter and run.
g = create_graph()
layouter = OrthogonalLayouter(g)
layouter.run()

# Draw the original graph.
init_pyplot((20, 3))
nx.draw_networkx(layouter.g, pos=layouter.pos)

# Draw each polygon with its orthogonal vertex positions.
buff = 1
x_margin = max([p[0] for p in layouter.pos.values()]) + buff
for poly in layouter.polys:
    poss = poly.vertex_positions()#nx.get_node_attributes(poly.g, POSITION)
    print poss
    old_poss = poss.copy()
    for nidx, p in poss.items():
        p[0] += x_margin
        #p[1] += y_margin
    x_margin = max([p[0] for p in old_poss.values()]) + buff

    fg = nx.Graph()
    fg.add_edges_from(poly)
    nx.draw_networkx(fg, poss)

# Show all.
plt.show()