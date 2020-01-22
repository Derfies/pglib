import itertools as it

import enum
import networkx as nx
import matplotlib.pyplot as plt


NUM_NODES = 5
INSIDE_CORNER = 90
OUTSIDE_CORNER = -90
STRAIGHT_CORNER = 0


class Direction(enum.IntEnum):
    up = 0
    right = 1
    down = 2
    left = 3


X_DIRS = (Direction.left, Direction.right)
Y_DIRS = (Direction.up, Direction.down)


class Layout(object):

    def __init__(self, g, angles):
        self.g = g
        self.angles = angles
        self.edges = self._get_face_edges()
        self.calculate_bounds()

    def _get_face_edges(self):
        """
        Return contiguous face edges.
        """
        def get_first_edge(n):
            return list(self.g.edges(n))[0]
        x = list(self.g.nodes())[0]
        edges = [get_first_edge(x)]
        while edges[-1][1] != x:
            edges.append(get_first_edge(edges[-1][1]))
        return edges

    def calculate_bounds(self):

        edges = {}
        print '\nangles:', self.angles
        direction = Direction.up
        for idx, edge in enumerate(self.edges):
            print '    ', idx, edge, direction
            edges.setdefault(direction, []).append(edge)
            if self.angles[idx] == INSIDE_CORNER:
                direction += 1
            elif self.angles[idx] == OUTSIDE_CORNER:
                direction -= 1
            direction = Direction(int(direction) % 4)

        print 'edges:'#, edges
        for dir_, idx in edges.items():
            print '    ', dir_, idx

        # Calculate max bounds.
        self.x = max([len(idxs) for dir_, idxs in edges.items() if dir_ in X_DIRS])
        self.y = max([len(idxs) for dir_, idxs in edges.items() if dir_ in Y_DIRS])


def permute_layouts(g):

    # We need four inside corners in order to close the polygon.
    num_nodes = g.number_of_nodes()
    num_spare_nodes = num_nodes - 4

    # Calculate all possible combinations of spare angles. Filter out all
    # combinations that do not add up to zero, as these will leave the polygon
    # unclosed.
    spare_angle_perms = filter(lambda x: sum(x) == 0, it.product([
        INSIDE_CORNER, 
        OUTSIDE_CORNER, 
        STRAIGHT_CORNER
    ], repeat=num_spare_nodes))

    # Calculate all possible positions of the minimum four required inside
    # corners.
    inside_angle_perms = [
        tuple([
            INSIDE_CORNER if idx not in idxs else None # Do we need to do outside corner?
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

    # Walk polygon edges clockwise and put into buckets.

    for angles in set(angle_perms):
        layout = Layout(g, angles)
        print 'x:', layout.x
        print 'y:', layout.y


# Outright fail if there are less than 4 nodes. We can change this to try to
# insert new dummy nodes in the future.
g = nx.path_graph(NUM_NODES, create_using=nx.DiGraph)
assert g.number_of_nodes() >= 4, 'Cannot close polygon with less than 4 nodes'

# Add an edge from the last to the first node to create an enclosed polygon.
nodes = list(g.nodes())
g.add_edge(nodes[-1], nodes[0])
permute_layouts(g)
