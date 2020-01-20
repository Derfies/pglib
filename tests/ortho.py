import itertools as it
import matplotlib.pyplot as plt

import networkx as nx


NUM_NODES = 8
INSIDE_CORNER = 90
OUTSIDE_CORNER = -90
STRAIGHT_CORNER = 0


def permute_layouts(g):

    # We need four inside corners in order to close the polygon.
    num_nodes = g.number_of_nodes()
    num_spare_nodes = num_nodes - 4

    # Calculate all possible combinations of interior angles. In order for the 
    # polygon to be closed these must add up to zero.
    all_int_angles = list(it.product([
        INSIDE_CORNER, 
        OUTSIDE_CORNER, 
        STRAIGHT_CORNER
    ], repeat=num_spare_nodes))
    int_angles = filter(lambda x: sum(x) != 0, all_int_angles)

    angle_groups = []
    spare_node_idx_groups = list(it.combinations(range(num_nodes), num_spare_nodes))
    for spare_node_idxs in spare_node_idx_groups:
        angles = tuple([
            INSIDE_CORNER if idx not in spare_node_idxs else number_of_nodes # Do we need to do outside corner?
            for idx in range(num_nodes)
        ])
        angle_groups.append(angles)

        #for angles in angle_groups:
        print angles, len(spare_node_idxs)

    print len(angle_groups)
    print len(set(angle_groups))


g = nx.path_graph(NUM_NODES)

# Outright fail if there are less than 4 nodes. We can change this to try to 
# insert new dummy nodes in the future.
assert g.number_of_nodes() >= 4, 'Cannot close polygon with less than 4 nodes'
nodes = list(g.nodes())
g.add_edge(nodes[0], nodes[-1])
#nx.draw(g, pos=nx.spring_layout(g))
#plt.show()
permute_layouts(g)
