import copy
import pyglet
import pygraph
import logging

from pygprim.context import line, rect, text


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


GRID = 40
OFFSET = 100
VERTEX_STROKEWIDTH = 5
VERTEX_STROKE = (1, 0, 0, 0)
EDGE_STROKEWIDTH = 5
EDGE_STROKE = (0, 1, 0, 0)
WIN_WIDTH = 640
WIN_HEIGHT = 480


class Line(object):
    
    def __init__(self, x1, y1, x2, y2, stroke, strokewidth, id_):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.stroke = stroke
        self.strokewidth = strokewidth
        self.id = id_

    def draw(self, font_size=12, text_offset=None):
        line(
            self.x1 * GRID + OFFSET, 
            WIN_HEIGHT - (self.y1 * GRID + OFFSET),  
            self.x2 * GRID + OFFSET,  
            WIN_HEIGHT - (self.y2 * GRID + OFFSET), 
            stroke=self.stroke, 
            strokewidth=self.strokewidth
        )

        text_offset = text_offset or (-20, 0)
        label = pyglet.text.Label(str(self.id),
            font_name='Times New Roman',
            font_size=font_size,
            x=self.x1 * GRID + OFFSET + text_offset[0], 
            y=WIN_HEIGHT - (self.y1 * GRID + OFFSET + text_offset[1]), 
            anchor_x='center', anchor_y='center'
        )
        label.draw()

    # def copy(self):
    #     return self.__class__(
    #         self.x1,
    #         self.y1,
    #         self.x2,
    #         self.y2,
    #         self.stroke,
    #         self.strokewidth,
    #         self.id,
    #     )


class Vertex(Line):

    def __init__(self, x, y, width, id_, **kwargs):
        x1, x2 = x, x + width
        y1, y2 = y, y
        super(Vertex, self).__init__(x1, y1, x2, y2, VERTEX_STROKE, VERTEX_STROKEWIDTH, id_, **kwargs)

        self.edges = []

    @property
    def width(self):
        return self.x2 - self.x1

    @width.setter
    def width(self, width):
        self.x2 = self.x1 + width

    @property
    def x(self):
        return self.x1

    @property
    def y(self):
        return self.y1

    def overlaps(self, other):
        return self.x1 < other.x2 and self.x2 > other.x1

    def is_connected(self, other):
        return any([
            self in edge.vertices 
            for edge in other.edges
        ])

    def collides_with_edge(self, edge):
        return edge.x > self.x1 and edge.x < self.x2


        
class Edge(Line):

    #def __init__(self, x, y1, y2, id_, **kwargs):
    def __init__(self, v1, v2):
        x1, x2 = v2.x + 0.5, v2.x + 0.5
        y1, y2 = v1.y, v2.y
        #y1, y2 = y, y + height
        super(Edge, self).__init__(x1, y1, x2, y2, EDGE_STROKE, EDGE_STROKEWIDTH, str(v1.id) + '|' + str(v2.id))

        self.vertices = (v1, v2)
        v1.edges.append(self)
        v2.edges.append(self)

    @property
    def x(self):
        return self.x1


class VisibilityGraphGenerator(object):

    def __init__(self, graph):
        self.graph = graph
        
        self.y = 0
        self.processed = []

        self.vertices = {}
        self.edges = []

    def push_right(self, pos, amt):
        for vertex in self.vertices.values():
            if pos < vertex.x2:
                vertex.x2 += amt
            if pos <= vertex.x1:
                vertex.x1 += amt

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

            # Ensure the two vertices overlap.
            if not vertex.overlaps(conn_vertex):

                # We need to extend the vertex so there's an overlap point to
                # draw and edge, but there might be an edge in the way.
                new_x = conn_vertex.x1 + 1
                test_vertex = vertex.copy()
                test_vertex.width += new_x
                for vertex in self.vertices.values():
                    for edge in vertex.edges:
                        print test_vertex.collides_with_edge(edge)

                #if collides:
                #    graph.Lengthen()
                logger.info('Extending: {} to: {}'.format(nidx, new_x))
                vertex.x2 = new_x

            # Create the edge to the original vertex.
            if not conn_vertex.is_connected(vertex):
                logger.info('Creating edge: {} -> {}'.format(nidx, conn_nidx))
                #edge = Edge(conn_vertex.x1, vertex.y1, conn_vertex.y1, str(nidx) + '|' + str(conn_nidx))
                #edge.vertices = (vertex, conn_vertex)
                edge = Edge(vertex, conn_vertex)
                
                self.edges.append(edge)
            # else:

            #     conn_vertex = self.vertices[conn_nidx]

            #     # See if we're connecting ahead.
            #     if conn_vertex.y > vertex.y:
            #         x2 = max(vertex.x1 + 1, conn_vertex.x2)
            #         logger.info('Lengthen: {} -> {}'.format(conn_nidx, x2))
            #         conn_vertex.x2 = x2

            #     if vertex.x2 <= conn_vertex.x1:
            #         logger.info('here {} {}'.format(conn_vertex.x1, vertex.x1))
            #         #print 'here:', conn_vertex.x1, vertex.x1
            #     #else:


            # conn_vertex = self.vertices[conn_nidx]
            #self.edges.append(Edge(x + 0.5, vertex.y, conn_vertex.y - vertex.y))

        logger.info('')

    def run(self):
        i = 0
        #for nidx in pygraph.breadth_first_search(self.graph, root_node=1):
        # self.process_node(1)
        # self.process_node(2)
        # self.process_node(2)
            

        for nidx in pygraph.breadth_first_search(self.graph, root_node=1):
            self.process_node(nidx)
            i += 1
            if i > 1:
                break
        #    print nidx, self.graph.get_node(nidx), type(self.graph.get_node(nidx))
        #    #print dir(self.graph.get_node(nidx))




# Build graph.
square = pygraph.UndirectedGraph()
square.new_node()
square.new_node()
square.new_node()
square.new_node()
square.new_edge(1, 2)
square.new_edge(2, 3)
square.new_edge(3, 4)
square.new_edge(4, 1)

triangle = pygraph.UndirectedGraph()
triangle.new_node()
triangle.new_node()
triangle.new_node()
triangle.new_edge(1, 2)
triangle.new_edge(2, 3)
triangle.new_edge(3, 1)

graph2 = pygraph.UndirectedGraph()
graph2.new_node()
graph2.new_node()
graph2.new_node()
graph2.new_node()
graph2.new_edge(1, 2)
graph2.new_edge(2, 3)
graph2.new_edge(3, 1)

graph2.new_edge(4, 2)
graph2.new_edge(4, 3)
graph2.new_edge(4, 1)

# Run the generator.
graph_gen = VisibilityGraphGenerator(triangle)
graph_gen.run()

# Draw.
window = pyglet.window.Window(width=WIN_WIDTH, height=WIN_HEIGHT)

@window.event
def on_draw():
    for vertex in graph_gen.vertices.values():
        vertex.draw()
    for edge in graph_gen.edges:
        edge.draw(font_size=8, text_offset=(-20, GRID / 2))

pyglet.app.run()