import math
import logging
from collections import deque, defaultdict

import pyglet
import pygraph
import networkx as nx

import networkx01
from pygprim.context import line, rect, text


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


GRID = 40
OFFSET = 100
VERTEX_STROKEWIDTH = 6
VERTEX_STROKE = (1, 0, 0, 0)
EDGE_STROKEWIDTH = 4
EDGE_STROKE = (0, 1, 0, 0)
WIN_WIDTH = 640
WIN_HEIGHT = 560


class Line(object):

    def draw(self, **kwargs):
        offset = kwargs.pop('offset', (0, 0))
        line(
            self.x1 * GRID + OFFSET + offset[0], 
            WIN_HEIGHT - (self.y1 * GRID + OFFSET + offset[1]),  
            self.x2 * GRID + OFFSET + offset[0],  
            WIN_HEIGHT - (self.y2 * GRID + OFFSET + offset[1]),
            **kwargs
        )

        text_offset = kwargs.pop('text_offset', (0, 0))
        label = pyglet.text.Label(
            str(self.id),
            font_name='Times New Roman',
            font_size=kwargs.pop('font_size', 12),
            x=self.x1 * GRID + OFFSET + text_offset[0], 
            y=WIN_HEIGHT - (self.y1 * GRID + OFFSET + text_offset[1]), 
            anchor_x='center', anchor_y='center'
        )
        label.draw()


class Vertex(Line):

    def __init__(self, x1, x2, y, id_):
        self.x1 = x1
        self.x2 = x2
        self.y = y
        self.id = id_

        self.edges = []

    def __str__(self):
        return '({} - {}, {})'.format(self.x1, self.x2, self.y)

    @property
    def y1(self):
        return self.y

    @property
    def y2(self):
        return self.y

    def overlaps(self, other):
        return self.x1 < other.x2 and self.x2 > other.x1

    def is_connected(self, other):
        return any([
            self in (edge.v1, edge.v2) 
            for edge in other.edges
        ])

    def collides_with_edge(self, edge):
        return self.y > edge.y1 and self.y < edge.y2 and edge.x > self.x1 and edge.x < self.x2

    def draw(self, **kwargs):
        super(Vertex, self).draw(
            stroke=VERTEX_STROKE, 
            strokewidth=VERTEX_STROKEWIDTH,
            text_offset=(-10, 0),
        )

    def copy(self):
        return self.__class__(
            self.x1,
            self.x2,
            self.y,
            self.id
        )

    def get_next_available_column(self):
        edge_xs = [edge.x for edge in self.edges]
        for x in range(self.x1, self.x2):
            if x not in edge_xs:
                return x
        return None

        
class Edge(Line):

    def __init__(self, v1, v2, x):
        self.v1 = v1
        self.v2 = v2
        self.x = x#self.v1.x
        v1.edges.append(self)
        v2.edges.append(self)

    @property
    def id(self):
        return str(self.v1.id) + '|' + str(self.v2.id)

    @property
    def x1(self):
        return self.x

    @property
    def y1(self):
        return min(self.v1.y, self.v2.y)

    @property
    def x2(self):
        return self.x

    @property
    def y2(self):
        return max(self.v1.y, self.v2.y)

    def draw(self, **kwargs):
        super(Edge, self).draw(
            stroke=EDGE_STROKE,
            strokewidth=EDGE_STROKEWIDTH,
            offset=(GRID / 2, 0),
            text_offset=(5, 20),
            font_size=8,
        ) 


class VisibilityGraphGenerator(networkx01.CycleDfsIteratorBase):

    def __init__(self, alpha, *args, **kwargs):
        super(VisibilityGraphGenerator, self).__init__(*args, **kwargs)

        self.alpha = alpha
        self.x = 0
        self.y = 0
        self.vertices = {}
        self.edges = []


        self.counter = 0

    @property
    def width(self):
        return max([v.x2 for v in self.vertices.values()])

    def get_edges(self):
        edges = []
        for vertex in self.vertices.values():
            edges.extend(vertex.edges)
        return edges

    def insert_column(self, pos, amt=1):
        #logger.info('Widen from: {}'.format(pos))
        for vertex in self.vertices.values():
            if pos < vertex.x2:
                vertex.x2 += amt
                if pos <= vertex.x1:
                    vertex.x1 += amt
        for edge in self.edges:
            if pos <= edge.x:
                edge.x += amt
                #logger.info('Edge: {}.x2 -> {}'.format(edge.id, edge.x2))

    def insert_row(self, pos, amt=1):
        #print 'POS:', pos
        for vertex in self.vertices.values():
            if vertex.y > pos:
                vertex.y += amt
                #print vertex, 'vertex.y:', vertex.y

    def _create_vertex(self, x, idx):
        logger.info('    Creating vertex: {}'.format(idx))
        v = Vertex(x, x + 1, self.y, idx)
        self.vertices[idx] = v
        self.y += 1
        return v

    def get_or_create_vertex(self, x, idx):
        v = self.vertices.get(idx)
        if v is None:
            v = self._create_vertex(x, idx)
        return v


    def visit_edge(self, edge):

        edges = []
        x, y = edge
        edges.append(edge)
        e = list(self.g.edges(y))[0]
        edges.append(e)
        wk = y
        
        # print '    cycle:'
        # print '        e0:', e0
        # print '        e: ', e

        dfs_nums = self.g.nodes.data('dfs_num')
        while dfs_nums[e[1]] > dfs_nums[wk]:  # e is a tree edge
            wk = e[1]
            e = list(self.g.edges(wk))[0]
            edges.append(e)



        # For each edge in edges:
        # Get or create v1.
        # Get or create v2. 
        # Ensure overlap.
        # Build the edge.
        x = 0
        y = 0
        for e in edges:

            logger.info('Edge: {}'.format(e))

            # Get or create v1.
            v1 = self.vertices.get(e[0])
            if v1 is None:
                v1 = Vertex(x, x + 1, y, e[0])
                self.vertices[e[0]] = v1
                y += 1
            else:
                x = v1.get_next_available_column()
                if x is None:

                    # This is currently "GO RIGHT". Need to do "GO LEFT".
                    x = v1.x2
                    logger.info('    Insert col: {}'.format(x))
                    self.insert_column(x)
                        
                    # TODO:
                    # Don't insert row if the second vert already exists.
                    logger.info('    Insert row: {}'.format(v1))
                    self.insert_row(v1.y)
                    y = v1.y + 1

            # Get or create v2.
            if e[1] not in self.vertices:
                self.vertices[e[1]] = Vertex(x, x + 1, y, e[1])
                y += 1
            v2 = self.vertices[e[1]]

            # Ensure both vertices overlap the current column.
            v1.x1 = min(v1.x1, x)
            v1.x2 = max(v1.x2, x + 1)
            v2.x1 = min(v2.x1, x)
            v2.x2 = max(v2.x2, x + 1)
            logger.info('    Vertex: {} -> {}'.format(e[0], v1))
            logger.info('    Vertex: {} -> {}'.format(e[1], v2))

            #logger.info('    Next avail: {} {}'.format(v1.get_next_available_column(), x))

            # Create the edge for this column.
            self.edges.append(Edge(v1, v2, x))
            logger.info('    Edge: {} -> {}'.format(self.edges[-1].id, x))

            x += 1

            #if e == ('N10', 'N3'):
            #    return
            
        #return
            

        if self.counter > 0:
           return
        self.counter += 1



        dfs_nums = self.g.nodes.data('dfs_num')
        parents = self.g.nodes.data('parent')
        x, w, w0 = self.find_cycle(edge)



        stack = []
        while w != x:

            #print '->', w, parents[w]

            for i, e in enumerate(list(self.g.edges(w))):

                # No action for first edge.
                if i == 0:
                    continue

                if dfs_nums[w] < dfs_nums[e[1]]: 
                    if not self.visit_edge(e):
                        return False

            w = parents[w]

        return True


                #else:

    # def breadth_first_search(self, root_node, first_node):

    #     ordering = []

    #     all_nodes = self.graph.get_all_node_ids()
    #     #if not all_nodes:
    #     #    return ordering

    #     queue = deque()
    #     discovered = defaultdict(lambda: False)
    #     to_visit = set(all_nodes)

    #     # if root_node is None:
    #     #     root_node = all_nodes[0]

    #     #discovered[root_node] = True
    #     #queue.appendleft(root_node)
    #     discovered[first_node] = True
    #     queue.appendleft(first_node)

    #     # We need to make sure we visit all the nodes, including disconnected ones
    #     #while True:
    #         # BFS Main Loop
    #     while len(queue) > 0:
    #         current_node = queue.pop()
    #         ordering.append(current_node)
    #         to_visit.remove(current_node)

    #         for n in self.graph.neighbors(current_node):
    #             if not discovered[n] and n != root_node:
    #                 discovered[n] = True
    #                 queue.appendleft(n)

            # # New root node if we still have more nodes
            # if len(to_visit) > 0:
            #     node = to_visit.pop()
            #     to_visit.add(node)  # --We need this here because we remove the node as part of the BFS algorithm
            #     discovered[node] = True
            #     queue.appendleft(node)
            # else:
            #     break

    #    return ordering

    # def process_node(self, idx):

        
    #     vertex = self.vertices[idx]
    #     logger.info('Vertex: {} x: {}'.format(idx, vertex.x2))

    #     # Iterate connected nodes.
    #     neighbours = self.graph.neighbors(idx)

    #     edge_pos = {}
    #     for nidx in neighbours:

    #         nbr_drawn = nidx in self.vertices

    #         if nbr_drawn and self.vertices[nidx].is_connected(vertex):
    #             continue
    #         logger.info('Neighbour: {} already drawn: {}'.format(nidx, nbr_drawn))

    #         # for foo in self.breadth_first_search(idx, nidx):
    #         #     logger.info('  NEW -> {}'.format(foo))

    #         depth = 0
    #         #for test_idx in pygraph.depth_first_search(self.graph, root_node=nidx):
    #         for test_idx in self.breadth_first_search(idx, nidx):
    #             logger.info('  -> {}'.format(test_idx))
    #             if (test_idx == idx or 
    #             test_idx == nidx or 
    #             test_idx not in self.vertices or 
    #             self.vertices[test_idx].is_connected(vertex)):
    #                 depth += 1
    #                 continue

    #             #nbr_drawn2 = 1 if nbr_drawn else -1
                
    #             value = vertex.x2 - self.vertices[test_idx].x2
    #             logger.info('  want to connect:   {} x: {}'.format(test_idx, self.vertices[test_idx].x2))
    #             if math.copysign(1, value) < 0:
    #                 value += self.width
    #                 nbr_drawn = not nbr_drawn
                    
    #             logger.info('  after -> {}'.format(value))

    #             edge_pos[nidx] = (not nbr_drawn, value, -depth)
    #             break

    #     # TEST - Sort edge build order by what they have to connect with on the
    #     # board. This helps build loops without crossing edges.
    #     # edge_pos = {}
    #     # for test_idx in pygraph.breadth_first_search(self.graph, root_node=idx):

    #     #     # Don't worry about verts we haven't processed yet.
    #     #     if test_idx in self.vertices:
    #     #         edge_pos[test_idx] = self.vertices[test_idx].x1
    #     #print idx, '->', edge_pos

    #     # If edge pos is the same, prioritise nodes with longer search?

    #     logger.info('** {}'.format(edge_pos))
    #     neighbours.sort(key=lambda x: edge_pos.get(x, (0, 0, 0)))
    #     logger.info('** {}'.format(neighbours))
    #     for conn_idx in neighbours:

    #         #
    #         do_vertex = do_edge = False 
    #         if conn_idx not in self.vertices:
    #             do_vertex = do_edge = True
    #         elif not self.vertices[conn_idx].is_connected(vertex):
    #             do_edge = True

    #         if do_vertex or do_edge:

    #             logger.info('    Process neighbour: {}'.format(conn_idx))

    #             # Create the neighboring vertex.
    #             # BUG: This allows verts to be placed under one another. Need
    #             # to fix.
    #             x = vertex.get_next_available_column()
    #             logger.info('    Next available column idx: {}'.format(x))

    #             # Ensure the neighbour is at least as long as to create an overlap.
    #             if x is None:
                    
    #                 # Figure out if where to widen graph here...
    #                 x = vertex.x2

    #                 # Check collision here
    #                 do_widen = False
    #                 test_vertex = vertex.copy()
    #                 test_vertex.x2 += 1
    #                 for edge in sorted(self.get_edges(), key=lambda e: e.x):
    #                     if test_vertex.collides_with_edge(edge):
    #                         logger.info('Collides with edge: {} @ {}'.format(edge.id, edge.x))
    #                         do_widen = True
    #                         break
    #                 if do_widen:
    #                     logger.info('Widen graph at: {}'.format(x))
    #                     self.insert_column(x)

    #             if do_vertex:
    #                 self._create_vertex(x, self.y, conn_idx)

    #             # Ensure the two vertices overlap the column.
    #             conn_vertex = self.vertices[conn_idx]
    #             vertex.x1 = min(vertex.x1, x)
    #             vertex.x2 = max(vertex.x2, x + 1)
    #             conn_vertex.x1 = min(conn_vertex.x1, x)
    #             conn_vertex.x2 = max(conn_vertex.x2, x + 1)

    #             # HAXX
    #             for edge in sorted(self.get_edges(), key=lambda e: e.x):
    #                 if conn_vertex.collides_with_edge(edge):
    #                     logger.info('conn_vertex collides with edge: {} @ {}'.format(edge.id, edge.x))
    #                     conn_vertex.y = self.y
    #                     self.y += 1
    #                     break

    #             # Create the edge in the column to the original node.
    #             if do_edge:
    #                 logger.info('    Creating edge: {}|{} @ {}'.format(conn_idx, idx, x))
    #                 edge = Edge(conn_vertex, vertex, x)
    #                 self.edges.append(edge)
                
            
    #         if self.iters >= 4:
    #             return True
    #         self.iters += 1

    #     logger.info('')

    def run(self, source=None):
        if source is None:
            source = list(self.g.edges)[0]
        result = self.visit_edge(source)



g = nx.read_graphml(r'C:\Users\Jamie Davies\Documents\Graphs\test8.graphml')

# Bail if the graph isn't connected.
if not nx.is_connected(g):
    raise Exception('Graph not connected!')

# Base planarity algorithm only works on biconnected components. Run the
# algorithm on each bicon separately then combine at the end.
itr = None
for bicons in nx.biconnected_components(g):
    dg = nx.DiGraph(nx.subgraph(g, bicons))
    itr = networkx01.process_biconnected_subgraph(dg)
    # = dg


print '*' * 35

print itr.alpha

graph_gen = VisibilityGraphGenerator(itr.alpha, itr.g)
graph_gen.run(('N1', 'N2'))

print 'done'

# Draw.
window = pyglet.window.Window(width=WIN_WIDTH, height=WIN_HEIGHT)

@window.event
def on_draw():
    for edge in graph_gen.edges:
        edge.draw(font_size=8, text_offset=(-20, GRID / 2))
    for vertex in graph_gen.vertices.values():
        vertex.draw()

pyglet.app.run()