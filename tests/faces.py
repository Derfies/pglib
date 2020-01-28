import math

import networkx as nx
import matplotlib.pyplot as plt

#from embedding import combinatorial_embedding_to_pos


GRID_PATH = r'C:\Users\Jamie Davies\Documents\Graphs\grid02.graphml'


def get_external_face(g, pos):
    #def left_most(G, pos):
    corner_node = min(pos, key=lambda k: (pos[k][0], pos[k][1]))
    other = max(
        g.adj[corner_node], key=lambda node:
        (pos[node][1] - pos[corner_node][1]) /
        math.hypot(
            pos[node][0] - pos[corner_node][0],
            pos[node][1] - pos[corner_node][1]
        )
    )  # maximum cosine value
    return sorted([corner_node, other], key=lambda node:
                  (pos[node][1], pos[node][0]))

    #if len(self.pos) < 2:
    #    return list(self.dcel.face_dict.values())[0]
    #down, up = left_most(g, pos)
    #print down, up
        #return self.dcel.half_edge_dict[up, down].inc


def convert_pos_to_embdeding(G, pos):
    '''only straight line in G.
    '''
    emd = nx.PlanarEmbedding()
    for node in G:
        neigh_pos = {
            neigh: (pos[neigh][0]-pos[node][0], pos[neigh][1]-pos[node][1]) for neigh in G[node]
        }
        neighes_sorted = sorted(G.adj[node],
                                key=lambda v: math.atan2(
                                    neigh_pos[v][1], neigh_pos[v][0])
                                )  # counter clockwise
        last = None
        for neigh in neighes_sorted:
            emd.add_half_edge_ccw(node, neigh, last)
            last = neigh
    emd.check_structure()
    return emd


def Faces(edges,embedding): 
    """
    edges: is an undirected graph as a set of undirected edges
    embedding: is a combinatorial embedding dictionary. Format: v1:[v2,v3], v2:[v1], v3:[v1] clockwise ordering of neighbors at each vertex.)

    """

    # Establish set of possible edges
    edgeset = set()
    for edge in edges: # edges is an undirected graph as a set of undirected edges
        edge = list(edge)
        edgeset |= set([(edge[0],edge[1]),(edge[1],edge[0])])

    # Storage for face paths
    faces = []
    path  = []
    for edge in edgeset:
        path.append(edge)
        edgeset -= set([edge])
        break  # (Only one iteration)

    # Trace faces
    while (len(edgeset) > 0):
        neighbors = embedding[path[-1][-1]]
        #print neighbors
        next_node = neighbors[(neighbors.index(path[-1][-2])+1)%(len(neighbors))]
        tup = (path[-1][-1],next_node)
        if tup == path[0]:
            faces.append(path)
            path = []
            for edge in edgeset:
                path.append(edge)
                edgeset -= set([edge])
                break  # (Only one iteration)
        else:
            path.append(tup)
            edgeset -= set([tup])
    if (len(path) != 0): faces.append(path)
    return iter(faces)


def traverse(graph, embedding):

    next_edge = {}
    visited = {}
    for edge in graph.edges:
        next_edge[edge] = {}
        visited[edge] = set()

    for source in graph.nodes:
        node_embedding = embedding[source]
        for i, target in enumerate(node_embedding):
            edge = (source, target)
            following_edge = (source, node_embedding[i + 1] if i != len(node_embedding) - 1 else node_embedding[0])
            if edge in next_edge:
                next_edge[edge][source] = following_edge
            else:
                next_edge[switch_edge(edge)][source] = following_edge

    self_loops = []
    #edges_cache = []
    #vertices_in_edge = []

    # for edge in graph.edges:
    #     edges_cache.append(edge)
    #     if edge[0] == edge[1]:
    #         self_loops.append(edge)
    
    faces = []
    for e in list(graph.edges):
        #del vertices_in_edge[:]
        #vertices_in_edge.append(e[0])
        #vertices_in_edge.append(e[1])

        for n in e:#vertices_in_edge:
            edge_visited = get_correct_edge_value(visited, e)
            begin_face = False

            if n not in edge_visited:
                #print 'begin face'
                faces.append([])
                begin_face = True

            

            while n not in edge_visited:
                faces[-1].append(n)
                edge_visited.add(n)
                n = e[1] if e[0] == n else e[0]
                e = get_correct_edge_value(next_edge, e)[n]
                edge_visited = get_correct_edge_value(visited, e)

    for face in faces:
        print '->', face
            

    #         if begin_face:
    #             print 'end face'
            
    # # Iterate over all self-loops, visiting them once separately
    # # (they've already been visited once, this visitation is for
    # # the "inside" of the self-loop)
    # for edge in self_loops:
    #     visitor.begin_face()
    #     visitor.next_edge(edge)
    #     visitor.NextNode(edge.Source)
    #     visitor.EndFace()
    
    # visitor.EndTraversal()


def switch_edge(edge):
    return (edge[1], edge[0])


def get_correct_edge_value(dictionary, edge):
    if edge in dictionary:
        return dictionary[edge]
    return dictionary[switch_edge(edge)]


#g = nx.Graph(nx.read_graphml(GRID_PATH)).to_directed()
g = nx.read_graphml(GRID_PATH)




#for edge in g.edges():
#    print '->', edge
# print type(g)
# for edge in g.edges:
#     print '->', edge
print ''
is_planar, embedding = nx.check_planarity(g)

pos = nx.spring_layout(g)
embedding = convert_pos_to_embdeding(g, pos)

print 'EXT Face:', get_external_face(g, pos)


foo = Faces(g.edges(), embedding.get_data())
for f in foo:
    print '*', f
print ''
# for foo, bar in embedding.items():
#     print foo, bar

# for d in dir(embedding):
#     print d

#print embedding.number_of_edges()
#for edge in embedding.edges():
#    print '->', edge

# for e in g.edges():
#     print '->', e

# print ''
visited = set()
for e in embedding.edges():
    if e in visited:
        print 'skip:', e
        continue

    print '&', embedding.traverse_face(*e, mark_half_edges=visited)

#print '*' * 35
#for e in embedding.edges():
#    print e
print ''
embedding_data = embedding.get_data()
traverse(g, embedding_data)

faces = []
visited = set()
#edge = list(g.edges)[0]
# for edge in list(g.edges):
    # if edge in visited:
    #     continue
print ''

#for i in range(2):
for edge in list(g.edges):
    #m = 0
    #print edge, visited

    if edge not in visited:
        faces.append([])

    next_edge = edge
    while edge not in visited:

        #m += 1
        #print 'visit:', next_edge
        faces[-1].append(next_edge)
        source, target = next_edge
        index = embedding_data[target].index(source) - 1
        index = index % len(embedding_data[target])
        next_edge = (target, embedding_data[target][index])
        visited.add(next_edge)

        # if m > 10:
        #     print 'BROKEN'
        #     break
    #edge = (next_edge[1], next_edge[0])
    #print 'EDGE NOW:', edge


for face in faces:
    print '#', face




nx.draw_networkx(g, pos=pos)
plt.show()