import pyglet
import pygraph
import logging

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
WIN_HEIGHT = 480


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

    def __init__(self, x, y, width, id_):
        self.x = x
        self.y = y
        self.width = width
        self.id = id_

        self.edges = []

    @property
    def x1(self):
        return self.x

    @x1.setter
    def x1(self, x1):
        self.x = x1

    @property
    def y1(self):
        return self.y

    @property
    def x2(self):
        return self.x + self.width

    @x2.setter
    def x2(self, x2):
        self.width = x2 - self.x1

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
        # logger.info('    self.y: {}'.format(self.y))
        # logger.info('    edge.y1: {}'.format(edge.y1))
        # logger.info('    edge.y2: {}'.format(edge.y2))
        # logger.info('    self.y > edge.y1: {}'.format(self.y > edge.y1))
        # logger.info('    self.y < edge.y2: {}'.format(self.y < edge.y2))
        # logger.info('    edge.x > self.x1: {}'.format(edge.x > self.x1))
        # logger.info('    edge.x < self.x2: {}'.format(edge.x < self.x2))
        return self.y > edge.y1 and self.y < edge.y2 and edge.x > self.x1 and edge.x < self.x2

    def draw(self, **kwargs):
        super(Vertex, self).draw(
            stroke=VERTEX_STROKE, 
            strokewidth=VERTEX_STROKEWIDTH,
            text_offset=(-10, 0),
        )

    def copy(self):
        return self.__class__(
            self.x,
            self.y,
            self.width,
            self.id
        )

        
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
        return self.x#(self.v1.x1 + self.v1.x2) / 2.0

    @property
    def y1(self):
        return min(self.v1.y, self.v2.y)

    @property
    def x2(self):
        return self.x#(self.v2.x1 + self.v2.x2) / 2.0

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


class VisibilityGraphGenerator(object):

    def __init__(self, graph):
        self.graph = graph
        
        self.y = 0
        self.processed = []

        self.vertices = {}
        self.edges = []


        self.iters = 0

    def get_edges(self):
        edges = []
        for vertex in self.vertices.values():
            edges.extend(vertex.edges)
        return edges

    def widen_from(self, pos, amt=1):
        logger.info('Widen from: {}'.format(pos))
        for vertex in self.vertices.values():
            if pos < vertex.x1:
                vertex.x1 += amt
                logger.info('Vertex: {}.x1 -> {}'.format(vertex.id, vertex.x1))
            elif pos < vertex.x2:
                vertex.x2 += amt
                logger.info('Vertex: {}.x2 -> {}'.format(vertex.id, vertex.x2))
            logger.info('Vertex : {}.width -> {}'.format(vertex.id, vertex.width))

        for edge in self.edges:
            if pos <= edge.x:
                edge.x += amt
                logger.info('Edge: {}.x2 -> {}'.format(edge.id, edge.x2))

    def process_node(self, nidx):

        logger.info('{} Process: {}'.format('*' * 5, nidx))
        
        neighbours = self.graph.neighbors(nidx)

        # Create the vertex.
        if nidx not in self.vertices:
            logger.info('Creating vertex: {}'.format(nidx))
            self.vertices[nidx] = Vertex(0, self.y, 1, nidx)
            self.y += 1
        vertex = self.vertices[nidx]

        # Create verts that are connected to the vert being processed.
        x = vertex.x1
        for conn_nidx in neighbours:
            logger.info('Process neighbour: {}'.format(conn_nidx))

            # Create the connected vertex.
            if conn_nidx not in self.vertices:
                logger.info('Creating vertex: {}'.format(conn_nidx))
                self.vertices[conn_nidx] = Vertex(x, self.y, 1, conn_nidx)
                self.y += 1
                x += 1
            conn_vertex = self.vertices[conn_nidx]

            # Ensure the neighbour is at least as long as to create an overlap.
            foo = max(conn_vertex.x2, vertex.x1 + 1)
            if foo != conn_vertex.x2:
                conn_vertex.x2 = foo
                logger.info('Lengthen: {}'.format(conn_vertex.x2))

            # Ensure the two vertices overlap.
            if not vertex.overlaps(conn_vertex):

                logger.info('Want to extend vertex: {}'.format(nidx))

                # We need to extend the vertex so there's an overlap point to
                # draw and edge, but there might be an edge in the way.
                new_x = conn_vertex.x1 + 1
                test_vertex = vertex.copy()
                test_vertex.width += new_x

                coll_x = None

                #for v in self.vertices.values():
                #    for edge in v.edges:
                for edge in sorted(self.get_edges(), key=lambda e: e.x):
                        #logger.info('test: {}'.format(edge.id))
                        if test_vertex.collides_with_edge(edge):
                            logger.info('Collides with edge: {} @ {}'.format(edge.id, edge.x))
                            coll_x = edge.x
                            break
                            #return True
                
                if coll_x:
                    self.widen_from(coll_x)
                
                logger.info('Extending vertex: {} to: {}'.format(nidx, new_x))
                vertex.x2 = new_x

            # Create the edge to the original vertex.
            if not conn_vertex.is_connected(vertex):
                logger.info('Creating edge: {}|{}'.format(conn_nidx, nidx))
                edge = Edge(conn_vertex, vertex, max(conn_vertex.x1, vertex.x1))
                self.edges.append(edge)

            self.iters += 1

            if self.iters > 4:
                return True

        logger.info('')

    def run(self):
        #i = 0
        for nidx in pygraph.breadth_first_search(self.graph, root_node=1):
            result = self.process_node(nidx)
            if result:
               break
            #i += 1
            #if i > 1:
            #    break


# Build graph.
ln = pygraph.UndirectedGraph()
ln.new_node()
ln.new_node()
ln.new_edge(1, 2)

fork = pygraph.UndirectedGraph()
fork.new_node()
fork.new_node()
fork.new_node()
fork.new_node()
fork.new_edge(1, 2)
fork.new_edge(1, 3)
fork.new_edge(1, 4)

tri = pygraph.UndirectedGraph()
tri.new_node()
tri.new_node()
tri.new_node()
tri.new_edge(1, 2)
tri.new_edge(2, 3)
tri.new_edge(3, 1)

square = pygraph.UndirectedGraph()
square.new_node()
square.new_node()
square.new_node()
square.new_node()
square.new_edge(1, 2)
square.new_edge(2, 3)
square.new_edge(3, 4)
square.new_edge(4, 1)

rect = pygraph.UndirectedGraph()
rect.new_node()
rect.new_node()
rect.new_node()
rect.new_node()
rect.new_node()
rect.new_node()
rect.new_edge(1, 2)
rect.new_edge(2, 3)
rect.new_edge(3, 4)
rect.new_edge(4, 5)
rect.new_edge(5, 6)
rect.new_edge(6, 1)

tee = pygraph.UndirectedGraph()
tee.new_node()
tee.new_node()
tee.new_node()
tee.new_node()
tee.new_edge(1, 2)
tee.new_edge(2, 3)
tee.new_edge(2, 4)

tee2 = pygraph.UndirectedGraph()
tee2.new_node()
tee2.new_node()
tee2.new_node()
tee2.new_node()
tee2.new_node()
tee2.new_node()
tee2.new_node()
tee2.new_edge(1, 2)
tee2.new_edge(2, 3)
tee2.new_edge(2, 4)
tee2.new_edge(4, 5)
tee2.new_edge(4, 6)
tee2.new_edge(4, 7)

tripyr = pygraph.UndirectedGraph()
tripyr.new_node()
tripyr.new_node()
tripyr.new_node()
tripyr.new_node()
tripyr.new_edge(1, 2)
tripyr.new_edge(2, 3)
tripyr.new_edge(3, 1)
tripyr.new_edge(4, 2)
tripyr.new_edge(4, 3)
tripyr.new_edge(4, 1)

# Run the generator.
graph_gen = VisibilityGraphGenerator(tripyr)
graph_gen.run()

# Draw.
window = pyglet.window.Window(width=WIN_WIDTH, height=WIN_HEIGHT)

@window.event
def on_draw():
    
    for edge in graph_gen.edges:
        edge.draw(font_size=8, text_offset=(-20, GRID / 2))
    for vertex in graph_gen.vertices.values():
        vertex.draw()

pyglet.app.run()