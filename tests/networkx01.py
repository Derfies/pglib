import networkx as nx


LEFT = 0
RIGHT = 1


class Block(object):

    def __init__(self, e, A):
        self.l_att = []
        self.r_att = [] 
        self.l_seg = []
        self.r_seg = [] 

        self.l_seg.append(e)
        self.l_att.extend(A)
            
    def flip(self):
        self.r_att, self.l_att = self.l_att, self.r_att
        self.r_seg, self.l_seg = self.l_seg, self.r_seg
        
    def left_interlace(self, s):
        return s and s[-1].l_att and self.l_att[-1] < s[-1].l_att[0]

    def right_interlace(self, s):
        return s and s[-1].r_att and self.l_att[-1] < s[-1].r_att[0]
            
    def combine(self, block):
        self.l_att.extend(block.l_att)
        self.r_att.extend(block.r_att)
        self.l_seg.extend(block.l_seg)
        self.r_seg.extend(block.r_seg)
        
    def clean(self, dfs_num_w, alpha, dfs_num):

        while self.l_att and self.l_att[0] == dfs_num_w:
            self.l_att.pop(0)
        while self.r_att and self.r_att[0] == dfs_num_w:
            self.r_att.pop(0)

        if self.l_att or self.r_att:
            return False
            
        for e in self.l_seg:
            alpha[e] = LEFT
        for e in self.r_seg:
            alpha[e] = RIGHT 
            
        return True
        
    def add_to_att(self, Att, dfs_num_w0, alpha, dfs_num):

        if self.r_att and self.r_att[0] > dfs_num_w0:
            self.flip()

        Att.extend(self.l_att)
        del self.l_att[:]
        Att.extend(self.r_att) 
        del self.r_att[:]

        for e in self.l_seg:
            alpha[e] = LEFT
        for e in self.r_seg:
            alpha[e] = RIGHT


class ReorderEdgesDfsIterator(object):

    def __init__(self, g):
        self.g = g

        self.dfs_num = 0
        self.visited = set()
        self.dfs_nums = {}
        self.parents = {}
        self.lowpt1s = {}
        self.lowpt2s = {}
        self.del_edges = []

    def visit_node(self, x):
        self.dfs_nums[x] = self.dfs_num
        self.lowpt1s[x] = self.lowpt2s[x] = self.dfs_num
        self.visited.add(x)
        self.dfs_num += 1

        # Calculate low point 1.
        edges = list(self.g.edges(x))
        edges.sort(key=lambda x: (len(x[1]), x[1]))     # TO DO: Remove this
        for edge in edges:
            y = edge[1]
            if y not in self.visited:
                self.parents[y] = x
                self.visit_node(y)
                self.lowpt1s[x] = min(self.lowpt1s[x], self.lowpt1s[y])
            else:
                self.lowpt1s[x] = min(self.lowpt1s[x], self.dfs_nums[y])
                if self.dfs_nums[y] >= self.dfs_nums[x] or y == self.parents[x]: 
                    self.del_edges.append(edge) 

        # Calculate low point 2.
        for edge in self.g.edges(x):
            y = edge[1]
            if self.parents.get(y) == x:
                if self.lowpt1s[y] != self.lowpt1s[x]:
                    self.lowpt2s[x] = min(self.lowpt2s[x], self.lowpt1s[y])
                self.lowpt2s[x] = min(self.lowpt2s[x], self.lowpt2s[y])
            else:
                if self.lowpt1s[x] != self.dfs_nums[y]:
                    self.lowpt2s[x] = min(self.lowpt2s[x], self.dfs_nums[y])

    def run(self, source=None):
        if source is None:
            source = list(self.g.nodes)[0]
        self.visit_node(source)


class StronglyPlanarDfsIterator(object):

    def __init__(self, g):
        self.g = g

        self.alpha = {}

    def find_cycle(self, e0):
        x, y = e0
        e = list(self.g.edges(y))[0]
        wk = y
        
        print '    cycle:'
        print '        e0:', e0
        print '        e: ', e

        dfs_nums = self.g.nodes.data('dfs_num')
        while dfs_nums[e[1]] > dfs_nums[wk]:  # e is a tree edge
            wk = e[1]
            e = list(self.g.edges(wk))[0]
            print '        e: ', e
        w0 = e[1]
        print '        wk (last node on tree path):', wk
        print '        w0 (back edge destination):', w0

        w = wk

        return x, w, w0

    def visit_edge(self, edge, att):

        x, w, w0 = self.find_cycle(edge)
        
        dfs_nums = self.g.nodes.data('dfs_num')
        dfs_parents = self.g.nodes.data('dfs_parent')

        stack = []
        while w != x:
            for i, e in enumerate(list(self.g.edges(w))):

                # No action for first edge.
                if i == 0:
                    continue

                a = []
                if dfs_nums[w] < dfs_nums[e[1]]: 
                    if not self.visit_edge(e, a):
                        return False                    
                else:
                    a.append(dfs_nums[e[1]])
                    
                block = Block(e, a)
                while True:
                    if block.left_interlace(stack): 
                        stack[-1].flip()
                    if block.left_interlace(stack): 
                        return False
                    if block.right_interlace(stack): 
                        block.combine(stack.pop())
                    else: 
                        break
                stack.append(block)
                    
            while stack and stack[-1].clean(dfs_nums[dfs_parents[w]], self.alpha, dfs_nums):
                stack.pop()
                
            w = dfs_parents[w]
            
        del att[:]
        while stack:
            block = stack.pop()
            if block.l_att and block.r_att and block.l_att[0] > dfs_nums[w0] and block.r_att[0] > dfs_nums[w0]:
                return False
            block.add_to_att(att, dfs_nums[w0], self.alpha, dfs_nums)
            
        # Let's not forget that "w0" is an attachment of "S(e0)" except if w0 = x.
        if w0 != x: 
            att.append(dfs_nums[w0])

        print 'strongly_planar DONE:', edge, att
        print 'alpha:', self.alpha
        print ''
        
        return True

    def run(self, source=None):
        att = []
        if source is None:
            source = list(self.g.edges)[0]
        self.visit_edge(source, att)
        return att


def calculate_edge_weights(g):
    dfs_nums = g.nodes.data('dfs_num')
    lowpt1s = g.nodes.data('lowpt1')
    lowpt2s = g.nodes.data('lowpt2')
    for edge, edge_data in g.edges.items():
        x, y = edge
        if dfs_nums[y] < dfs_nums[x]:
            edge_data['weight'] = 2 * dfs_nums[y]
        elif lowpt2s[y] >= dfs_nums[x]:
            edge_data['weight'] = 2 * lowpt1s[y]
        else:
            edge_data['weight'] = 2 * lowpt1s[y] + 1


def process_biconnected_subgraph(g):
   
    # Create an iterator that will traverse the graph in a dfs manner, 
    # calculating dfs_num, lowpt1 and lowpt2 for each node.
    itr = ReorderEdgesDfsIterator(g)
    itr.run(source='N1')    # TO DO: Remove
    g.remove_edges_from(itr.del_edges)

    # Encode dfs_num and dfs_parent onto each node.
    nx.set_node_attributes(g, itr.dfs_nums, 'dfs_num')
    nx.set_node_attributes(g, itr.parents, 'dfs_parent')
    nx.set_node_attributes(g, itr.lowpt1s, 'lowpt1')
    nx.set_node_attributes(g, itr.lowpt2s, 'lowpt2')
    
    # Sort the edges based on their lowpt1 and lowpt2 values. Use an ordered
    # graph so the order can be maintained.
    og = nx.OrderedDiGraph()
    og.add_nodes_from(g.nodes(data=True))
    calculate_edge_weights(g)
    og.add_edges_from(sorted(g.edges(data=True), key=lambda e: e[2]['weight']))

    # Run the stronly planar function.
    itr = StronglyPlanarDfsIterator(og)
    itr.run(('N1', 'N2'))    # TO DO: Remove


def run(g):

    # Bail if the graph isn't connected.
    if not nx.is_connected(g):
        raise Exception('Graph not connected!')

    # Base planarity algorithm only works on biconnected components. Run the
    # algorithm on each bicon separately then combine at the end.
    for bicons in nx.biconnected_components(g):
        sg = nx.DiGraph(nx.subgraph(g, bicons))
        process_biconnected_subgraph(sg)


if __name__ == '__main__':
    g = nx.read_graphml(r'C:\Users\Jamie Davies\Documents\Graphs\test8.graphml')
    run(g)