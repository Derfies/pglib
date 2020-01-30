import math
import itertools as it

import enum
import networkx as nx
import matplotlib.pyplot as plt


NUM_NODES = 6
LENGTH = 'length'
ANGLE = 'angles'
GRID_PATH = r'test01.graphml'


class Direction(enum.IntEnum):

    up = 0
    right = 1
    down = 2
    left = 3

    @staticmethod
    def normalise(direction):
        return Direction(direction % 4)

    @staticmethod
    def opposite(direction):
        return Direction.normalise(direction - 2)

    @staticmethod
    def xs():
        return (Direction.left, Direction.right)

    @staticmethod
    def ys():
        return (Direction.up, Direction.down)


class Angle(enum.IntEnum):

    inside = 90
    outside = -90
    straight = 0


class Base(object):

    def edge_walk(self, direction):
        for edge in self.edges:
            yield edge, direction
            angle = self.g.node[edge[0]][ANGLE]
            if angle == Angle.inside:
                direction += 1
            elif angle == Angle.outside:
                direction -= 1
            direction = Direction.normalise(direction)


class Layout(Base):

    def __init__(self, face, angles):
        super(Base, self).__init__()

        self.g = nx.Graph()
        self.g.add_edges_from(face)
        nx.set_node_attributes(self.g, {
            node: {ANGLE: angles[idx] }
            for idx, node in enumerate(self.g.nodes)
        })
        nx.set_edge_attributes(self.g, 1, LENGTH)
        self.edges = face   # Edges are ordered at this point.
        self.edge_directions = self._get_edge_directions()

    def get_direction_length(self, direction):
        return sum([
            self.g[edge[0]][edge[1]][LENGTH]
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
        for edge, direction in list(self.edge_walk(Direction.up)):
            directions.setdefault(direction, []).append(edge)
        return directions

    def permute_polygons(self):
        """Permutes edge lengths"""

        polygons = []

        foobar = {}
        for axis in (Direction.xs(), Direction.ys()):
            lengths = {d: self.get_direction_length(d) for d in axis}
            min_dir = min(lengths, key=lengths.get)
            min_length, max_length = lengths[min_dir], lengths[Direction.opposite(min_dir)]
            all_length_perms = it.product(range(1, max_length + 1), repeat=min_length)
            length_perms = filter(lambda x: sum(x) == max_length, all_length_perms)
            foobar[min_dir] = length_perms
                      
        for perm in [dict(zip(foobar, v)) for v in it.product(*foobar.values())]:
            poly = Polygon(self.g, self.edges)
            for dir_, lengths in perm.items():
                for i, edge in enumerate(self.edge_directions[dir_]):
                    poly.g[edge[0]][edge[1]][LENGTH] = lengths[i]
            polygons.append(poly)

        return polygons


class Polygon(Base):

    def __init__(self, g, edges):
        super(Base, self).__init__()

        self.g = g.copy()
        self.edges = edges

    def vertex_positions(self):
        positions = {}
        pos = [0, 0]
        for edge, direction in list(self.edge_walk(Direction.up)):
            positions[edge[0]] = pos[:]
            length = self.g.edges[edge][LENGTH]
            if direction == Direction.up:
                pos[1] += length
            elif direction == Direction.right:
                pos[0] += length
            elif direction == Direction.down:
                pos[1] -= length
            else:   # Direction.left
                pos[0] -= length
        return positions


def permute_layouts(face):

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

    print 'total:', len(angle_perms)
    print 'unique:', len(set(angle_perms))
    return [Layout(face, angles) for angles in set(angle_perms)]


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
    
    
def convert_pos_to_embedding(g, pos):
    """only straight line in G."""
    emd = nx.PlanarEmbedding()
    for node in g:
        neigh_pos = {
            neigh: (
                pos[neigh][0] - pos[node][0],
                pos[neigh][1]-pos[node][1]
            ) for neigh in g[node]
        }
        neighes_sorted = sorted(
            g.adj[node],
            key=lambda v: math.atan2(
                neigh_pos[v][1], neigh_pos[v][0])
        )  # counter clockwise
        last = None
        for neigh in neighes_sorted:
            emd.add_half_edge_ccw(node, neigh, last)
            last = neigh
    emd.check_structure()
    return emd


def get_external_face_half_edge(g, pos):
    corner_node = min(pos, key=lambda k: (pos[k][0], pos[k][1]))
    other = max(
        g.adj[corner_node], key=lambda node:
        (pos[node][1] - pos[corner_node][1]) /
        math.hypot(
            pos[node][0] - pos[corner_node][0],
            pos[node][1] - pos[corner_node][1]
        )
    )  # maximum cosine value
    return (other, corner_node)


def get_faces(embedding):
    faces = []
    visited = set()
    for edge in embedding.edges():
        if edge in visited:
            continue
        nodes = embedding.traverse_face(*edge, mark_half_edges=visited)
        edges = []
        for idx in range(len(nodes)):
            next_idx = (idx + 1) % len(nodes)
            edges.append((nodes[idx], nodes[next_idx]))
        faces.append(edges)
    return faces


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


g = create_graph()
pos = nx.spring_layout(g, seed=0)
#nx.draw_networkx(g, pos=pos)
embedding = convert_pos_to_embedding(g, pos)

# Outright fail if any face is less than 4 edges. We can change this to try to
# insert new dummy nodes in the future.
faces = get_faces(embedding)
for face in faces:
    assert len(face) >= 4, 'Cannot close polygon with less than 4 nodes'

ext_hedge = get_external_face_half_edge(g, pos)
print 'ext_hedge:', ext_hedge
int_faces = filter(lambda x: ext_hedge not in x, faces)
sorted_faces = sorted(int_faces, key=lambda x: len(x))
print 'num faces:', len(sorted_faces)

init_pyplot((25, 3))

y_margin = 0
for face in sorted_faces:

    # Draw the original face.
    g = nx.Graph()
    g.add_edges_from(face)
    #nx.draw_networkx(g, pos=pos)


    layouts = permute_layouts(face)
    polys = []
    for layout in layouts:
        polys.extend(layout.permute_polygons())

    buff = 2
    x_margin = 0
    for i, poly in enumerate(polys):
        poss = poly.vertex_positions()
        old_poss = poss.copy()
        for nidx, p in poss.items():
            p[0] += x_margin
            p[1] += y_margin
        x_margin = max([p[0] for p in old_poss.values()]) + buff
        nx.draw_networkx(poly.g, pos=poss)

    y_margin = max([p[1] for p in old_poss.values()]) + buff

    #nx.draw_networkx(g, pos=pos)
plt.show()