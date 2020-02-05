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

from pglib.graph import const
from pglib.graph.face import Face
from pglib.graph.orthogonalmesh import OrthogonalMesh


NUM_NODES = 6
LENGTH = 'length'
ANGLE = 'angle'
POSITION = 'position'
DIRECTION = 'direction'
GRID_PATH = r'test01.graphml'


class NodeState(enum.IntEnum):

    unknown = 0
    free = 1
    known = 2


class OrthogonalFace(Face):

    def __init__(self, edges, angles, direction=const.Direction.up):
        super(OrthogonalFace, self).__init__(edges)

        self.angles = {
            node: angles[(idx) % len(self)]
            for idx, node in enumerate(self.nodes)
        }
        self.lengths = {edge: 1 for edge in self}

        #self.edges = face   # Edges are ordered at this point.
        self.edge_directions = self._get_edge_directions(direction)

    def get_direction_length(self, direction):
        return sum([
            self.lengths[edge]
            for edge in self.edge_directions[direction]
        ])
    
    # @property
    # def width(self):
    #     return max(map(self.get_direction_length, Direction.xs()))

    # @property
    # def height(self):
    #     return max(map(self.get_direction_length, Direction.ys()))

    def _get_edge_directions(self, direction):
        directions = {}
        self.directions = {}
        for edge, direction in list(self.edge_walk(direction)):
            #self.g[edge[0]][edge[1]][DIRECTION] = direction
            directions.setdefault(direction, []).append(edge)
            #self.g.edges[edge][DIRECTION] = direction
            self.directions[edge] = direction
        return directions

    def edge_walk(self, direction):
        for edge in self.edges:
            yield edge, direction
            angle = self.angles[edge[1]]#self.g.node[edge[1]][ANGLE]   # WRONG ANGLE BEING ENCODED
            if angle == const.Angle.inside:
                direction += 1
            elif angle == const.Angle.outside:
                direction -= 1
            direction = const.Direction.normalise(direction)

    def vertex_positions(self, direction):
        positions = {}
        pos = [0, 0]
        for edge, direction in list(self.edge_walk(direction)):
            positions[edge[0]] = pos[:]
            length = self.lengths[edge]#self.g.edges[edge][LENGTH]
            if direction == const.Direction.up:
                pos[1] += length
            elif direction == const.Direction.right:
                pos[0] += length
            elif direction == const.Direction.down:
                pos[1] -= length
            elif direction == const.Direction.left:
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

    def _sort_faces_by_num_nodes(self, faces):
        return sorted(faces, key=lambda n: len(n))

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

    def get_faces(self):
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

    def get_inner_faces(self):
        faces = self.get_faces()
        ext_hedge = self.get_external_face_half_edge()
        int_faces = filter(lambda x: ext_hedge not in x, faces)

        # Sort facees so we can walk through the mesh.
        sort_faces = self._sort_faces_by_num_nodes(int_faces)

        # Build edge -> face dict.
        self.edge_to_face = {}
        for face in sort_faces:
            for edge in face:
                self.edge_to_face.setdefault(edge, []).append(face)

        #for edge, faces in self.edge_to_face.items():
        #    print edge, '->', faces

        def rec_face(face, result):
            adj_faces = set()
            #print 'face:', face
            for rev_edge in face.reversed():
                adj_faces.update(self.edge_to_face.get(rev_edge, []))

            #  self._sort_faces_by_num_nodes([
                
               
            # ])
            for adj_face in self._sort_faces_by_num_nodes(adj_faces):
                #print '->', adj_face
                if adj_face not in result:
                    result.append(adj_face)    
                    rec_face(adj_face, result)

        result = [sort_faces[0]]
        rec_face(sort_faces[0], result)



        return result

    def _process_face(self, face_idx, g, indent):
        face = self.faces[face_idx]
        print ' ' * indent, 'Process face:', face

        #self.done_faces.append(face)

        face_added = False
        layouts = self.permute_layouts(g, face, indent)

        print ' ' * indent, 'Num layouts:', len(layouts)
        for i, layout in enumerate(layouts):

            print ' ' * indent, 'Eval layout:', i
            print ' ' * indent, 'Angles:', layout.angles

            # Test for layout validity here?
            g_copy = g.copy()

            can_join = g.can_add_face(layout)
            #print '    CAN JOIN:', can_join
            if not can_join:
                print ' ' * indent, 'Cannot join'
                #print ' ' * indent, poly.directions
                self.layouts.append(layout)
                continue
            else:
                print ' ' * indent, 'JOINED!'
                self.layouts.append(layout)
            g_copy.add_face(layout)
            g_copy.faces.append(face)
            g_copy.layouts.append(layout)
            #self.layouts.append(layout)
            face_added = True

            #return
          
            # Find adjoining faces.
            if face_idx < len(self.faces) - 1:
                result = self._process_face(face_idx + 1, g_copy, indent + 4)
                print ' ' * indent, 'adj:', result
            else:
                print 'FINISHED!'
                #self.final_layouts.append(g_copy)

        return face_added

    def run(self):
        #self.done_faces = []
        self.layouts = []
        self._process_face(0, OrthogonalMesh(), 0)


    def permute_layouts(self, g, face, indent):

        # Warning! These edges aren't guaranteed to be contiguous.
        poss_angles = []
        common_edges = g.get_common_edges(face)
        for node in face.nodes:
            idx = len(filter(lambda edge: node in edge, common_edges))
            node_state = NodeState(idx)
            if node_state == NodeState.known:
                poss_angles.append([g.get_explementary_angle(node)])
            elif node_state == NodeState.unknown:
                poss_angles.append(g.get_possible_angles(node))
            elif node_state == NodeState.free:
                poss_angles.append(list(const.Angle))
            else:
                raise Exception('Unknown node state: {}'.format(node_state))
            print ' ' * (indent + 2), node, node_state, poss_angles[-1]

        print '->', poss_angles

        #nodes, angles = poss_angles.keys(), poss_angles.values() 
        all_angle_perms = set(it.product(*poss_angles))
        angle_perms = filter(lambda x: sum(x) == 360, all_angle_perms)

        # Pick an edge-walk direction. If there's a common edge we need to use
        # that same edge's direction in order for the faces to join.
        walk_dir = const.Direction.up
        if common_edges:
            walk_dir = g.edges[common_edges[0]][DIRECTION]

        # Turn each set of 
        layouts = []
        for angles in angle_perms:

            # idx = len(angles)
            # foo = list(angles[idx:])
            # foo.extend(angles[0:idx])
            # angles = foo

            print 'INPUT'

            print 'walk_dir:', walk_dir

            for e in face.edges:
                print '-> e', e

            for a in angles:
                print '-> a', a

            layout = OrthogonalFace(face.edges, angles, walk_dir) 
            layouts.append(layout)


            print 'LAYOUT'

            for e in layout.edges:
                print '-> E', e

            

            for e, a in layout.angles.items():
                print '-> A', e, a

            #for edge, direction in list(layout.edge_walk(walk_dir)):
            #    print e, '->', direction


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

    g = nx.path_graph(NUM_NODES, create_using=nx.DiGraph)

    # Add an edge from the last to the first node to create an enclosed polygon.
    nodes = list(g.nodes())
    g.add_edge(nodes[-1], nodes[0])
    #g.add_edge(nodes[1], nodes[4])

    g.add_edge(nodes[1], '*')
    g.add_edge('*', nodes[4])

    '''

    g = nx.Graph(nx.read_graphml(GRID_PATH)).to_directed()
    '''
    return nx.Graph(nx.relabel_nodes(g, {
        n: chr(97 + n) for n in range(len(g.nodes()))
    })).to_directed()


# Create a test graph, pass it to a layouter and run.
g = create_graph()
layouter = OrthogonalLayouter(g)
layouter.run()

# Draw the original graph.
init_pyplot((10, 3))
nx.draw_networkx(layouter.g, pos=layouter.pos)

# Draw each polygon with its orthogonal vertex positions.
buff = 1
x_margin = max([p[0] for p in layouter.pos.values()]) + buff
for poly in layouter.layouts:
    poss = poly.vertex_positions(const.Direction.up)#nx.get_node_attributes(poly.g, POSITION)
    #print poss
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