import networkx as nx


class ReorderEdgesDfsIterator(object):

    def __init__(self, g):
        self.g = g

        self.depth = 0
        self.visited = set()
        self.depths = {}
        self.parents = {}
        self.lowpt1s = {}
        self.lowpt2s = {}

    def visit_node(self, x):

        print 'Node:', x, self.parents#, ', depth:', self.depth, ', edges:', self.g.edges(x)

        self.depths[x] = self.depth
        self.lowpt1s[x] = self.lowpt2s[x] = self.depth
        self.visited.add(x)
        self.depth += 1

        # Calculate low point 1.
        for edge in self.g.edges(x):
            y = edge[1]
            #print '    Node:', x, '    doing adj:', y
            if y not in self.visited:
                self.parents[y] = x
                self.visit_node(y)
                self.lowpt1s[x] = min(self.lowpt1s[x], self.lowpt1s[y])
                #print '    not visited node:', x, ', lowpt1s:', self.lowpt1s[x]
            else:
                self.lowpt1s[x] = min(self.lowpt1s[x], self.depths[y])
                #print '    visited node:', x, ', lowpt1s:', self.lowpt1s[x]

        # Calculate low point 2.
        for edge in self.g.edges(x):
            y = edge[1]
            print '    Node:', x, self.parents.get(y)
            if self.parents.get(y) == x:
                if self.lowpt1s[y] != self.lowpt1s[x]:
                    self.lowpt2s[x] = min(self.lowpt2s[x], self.lowpt1s[y])
                self.lowpt2s[x] = min(self.lowpt2s[x], self.lowpt2s[y])
            else:
                if self.lowpt1s[x] != self.depths[y]:
                    self.lowpt2s[x] = min(self.lowpt2s[x], self.depths[y])

    def run(self, source=None):
        if source is None:
            source = list(self.g)[0]
        self.visit_node(source)


def process_biconnected_subgraph(g):
    #print '*' * 35
    print type(g)
    ##print g.nodes()
    #print g.edges()

    dg = nx.DiGraph(g)

    #print len(g.edges())
    #print len(dg.edges())
    #print ''
    
    itr = ReorderEdgesDfsIterator(sg)
    itr.run('N1')

    #og = nx.DiGraph(g)
    #reorder_edges(dg)




def run(g):

    # Bail if the graph isn't connected.
    if not nx.is_connected(g):
        raise Exception('Graph not connected!')


    itr = ReorderEdgesDfsIterator(g)
    itr.run()

    for k in sorted(itr.lowpt1s):
        print k, '->', itr.lowpt1s[k]

    print '*' * 35

    for k in sorted(itr.lowpt2s):
        print k, '->', itr.lowpt2s[k]

    #reorder_edges(g)
    return

    # Base planarity algorithm only works on biconnected components. We'll run 
    # the algorithm on each bicon separately then combine at the end.
    for bicons in nx.biconnected_components(g):
        sg = nx.subgraph(g, bicons)
        process_biconnected_subgraph(sg)


if __name__ == '__main__':
    g = nx.read_graphml(r'C:\Users\Jamie Davies\Documents\Graphs\test11.graphml')
    run(g)