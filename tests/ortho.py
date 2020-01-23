import itertools as it

import enum
import networkx as nx
import matplotlib.pyplot as plt


NUM_NODES = 6
INSIDE_CORNER = 90
OUTSIDE_CORNER = -90
STRAIGHT_CORNER = 0
LENGTH = 'length'


class Direction(enum.IntEnum):
    up = 0
    right = 1
    down = 2
    left = 3

    @staticmethod
    def opposite(direction):
        return Direction((direction - 2) % 4)


X_DIRS = (Direction.left, Direction.right)
Y_DIRS = (Direction.up, Direction.down)



class Layout(object):

    def __init__(self, g, angles):
        self.g = g
        nx.set_edge_attributes(self.g, 1, LENGTH)
        self.angles = angles
        self.edges = self._get_face_edges()
        self.edge_directions = self._get_edge_directions()

        
        print self.width, self.height


        


    def get_direction_length(self, direction):
        return sum([
            self.g[edge[0]][edge[1]][LENGTH]
            for edge in self.edge_directions[direction]
        ])
    
    @property
    def width(self):
        return max(map(self.get_direction_length, X_DIRS))

    @property
    def height(self):
        return max(map(self.get_direction_length, Y_DIRS))

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

    def _get_edge_directions(self):

        edge_directions = {}
        print '\nangles:', self.angles
        direction = Direction.up
        for idx, edge in enumerate(self.edges):
            print '    ', idx, edge, direction
            edge_directions.setdefault(direction, []).append(edge)
            if self.angles[idx] == INSIDE_CORNER:
                direction += 1
            elif self.angles[idx] == OUTSIDE_CORNER:
                direction -= 1
            direction = Direction(int(direction) % 4)

        print 'edges:'#, edges
        for direction, idx in edge_directions.items():
            print '    ', direction, idx

        return edge_directions

        # Calculate max bounds.
        #self.x = max([len(idxs) for direction, idxs in edges.items() if direction in X_DIRS])
        #self.y = max([len(idxs) for direction, idxs in edges.items() if direction in Y_DIRS])

        #print 'width:', self.width
        #print 'height:', self.height

    def permute_polygons(self):

        polygons = []


        foobar = {}

        for axis in (X_DIRS, Y_DIRS):
            lengths = {d: self.get_direction_length(d) for d in axis}
            min_dir = min(lengths, key=lengths.get)
            min_length, max_length = lengths[min_dir], lengths[Direction.opposite(min_dir)]
            if True:#min_length != max_length:
                #print 'permute:', min_dir, min_length
                print 'min_dir:', min_dir
                # print 'opposite:', Direction.opposite(min_dir)
                # print 'min_length:', min_length
                # print 'max_length:', max_length
                # print 'permute:', min_dir
                # print 'num nodes available:', len(self.edge_directions[min_dir])
                # print 'required length:', max_length
                # print 'range:', range(1, max_length)
                # print 'product:', list(it.product(range(1, max_length + 1), repeat=min_length))

                #print list(it.product(range(1, max_length), repeat=len(self.edge_directions[min_dir])))
                all_length_perms = it.product(range(1, max_length + 1), repeat=min_length)
                length_perms = filter(lambda x: sum(x) == max_length, all_length_perms)


                foobar[min_dir] = length_perms#, []).append(length_perms)

                # for lengths in length_perms:
                #     print 'lengths:', lengths
                #     length_iter = iter(lengths)
                #     poly = Polygon(self.g.copy(), self.angles, self.edges)
                #     # #g = self.g.copy()
                #     for edge in self.edge_directions[min_dir]:
                #         poly.g[edge[0]][edge[1]][LENGTH] = length_iter.next()

                #     print poly.g.edges(data=True)
                #     print poly.vertex_positions()

                #     polygons.append(poly)
                      

        print 'foobar:', foobar
        for perm in [dict(zip(foobar, v)) for v in it.product(*foobar.values())]:
            #print '->', bar

            poly = Polygon(self.g.copy(), self.angles, self.edges)

            for dir_, lengths in perm.items():

                # for lengths in length_perms:
                #print 'lengths:', lengths
                length_iter = iter(lengths)
                
                # #g = self.g.copy()
                for edge in self.edge_directions[dir_]:
                    poly.g[edge[0]][edge[1]][LENGTH] = length_iter.next()

                #print poly.g.edges(data=True)
                #print poly.vertex_positions()

            polygons.append(poly)

        return polygons


class Polygon(object):

    def __init__(self, g, angles, edges):
        self.g = g
        self.angles = angles
        self.edges = edges

    def vertex_positions(self):
        positions = {}
        pos = [0, 0]

        direction = Direction.up
        for idx, edge in enumerate(self.edges):
            #print '    ', idx, edge, direction
            #edge_directions.setdefault(direction, []).append(edge)
            
            length = self.g[edge[0]][edge[1]][LENGTH]
            positions[idx] = pos[:]

            #next_pos = pos[:]
            if direction == Direction.up:
                pos[1] += length
            elif direction == Direction.right:
                pos[0] += length
            elif direction == Direction.down:
                pos[1] -= length
            else:   # Direction.left
                pos[0] -= length

            

            if self.angles[idx] == INSIDE_CORNER:
                direction += 1
            elif self.angles[idx] == OUTSIDE_CORNER:
                direction -= 1
            direction = Direction(int(direction) % 4)


        return positions


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
    polys = []
    for angles in set(angle_perms):
        layout = Layout(g.copy(), angles)
        polys.extend(layout.permute_polygons())

    return polys
        #for polygon in polygons:
        #    print 'polygon:', polygon.g.edges(data=True)


# Outright fail if there are less than 4 nodes. We can change this to try to
# insert new dummy nodes in the future.
g = nx.path_graph(NUM_NODES, create_using=nx.DiGraph)
assert g.number_of_nodes() >= 4, 'Cannot close polygon with less than 4 nodes'

# Add an edge from the last to the first node to create an enclosed polygon.
nodes = list(g.nodes())
g.add_edge(nodes[-1], nodes[0])

plt.figure(figsize=(25, 3))
#plt.margins(x=0, y=0)

# Then we set up our axes (the plot region, or the area in which we plot things).
# Usually there is a thin border drawn around the axes, but we turn it off with `frameon=False`.
ax = plt.axes([0,0,1,1], frameon=False)

# Then we disable our xaxis and yaxis completely. If we just say plt.axis('off'),
# they are still used in the computation of the image padding.
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

# Even though our axes (plot region) are set to cover the whole image with [0,0,1,1],
# by default they leave padding between the plotted data and the frame. We use tigher=True
# to make sure the data gets scaled to the full extents of the axes.
plt.autoscale(tight=True)

buff = 1
margin = 0
polys = permute_layouts(g)
for i, poly in enumerate(polys):
    poss = poly.vertex_positions()
    old_poss = poss.copy()
    
    for nidx, pos in poss.items():
        #print pos
        pos[0] += margin#(BUFFER * i)

    print '->', i, margin, poss

    margin = max([p[0] for p in old_poss.values()]) + 1 
    print 'margin now:', margin
        #pos[0] = pos[0] / len(polys)
    #for p in pos:
    #    print p
        #pos[0] += i
    nx.draw_networkx(poly.g, pos=poss)


plt.show()