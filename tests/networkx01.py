import abc

import networkx as nx


LEFT = 0
RIGHT = 1


class Block(object):

    def __init__(self, e, a):
        """
        Initialise the block with an edge and a list of attachments. This 
        represents a block with a single edge as the only segment in its left
        side.

        """
        self.l_att = []
        self.r_att = [] 
        self.l_seg = []
        self.r_seg = [] 

        self.l_seg.append(e)
        self.l_att.extend(a)
            
    def flip(self):
        """
        Interchange the two sides of a block by switching out the attachements
        and segments.

        """
        self.r_att, self.l_att = self.l_att, self.r_att
        self.r_seg, self.l_seg = self.l_seg, self.r_seg
        
    def left_interlace(self, s):
        """
        Return True if this block interlaces with the left side of the topmost 
        block of the given stack, False otherwise. 

        """
        return s and s[-1].l_att and self.l_att[-1] < s[-1].l_att[0]

    def right_interlace(self, s):
        """
        Return True if this block interlaces with the right side of the topmost 
        block of the given stack, False otherwise. 

        """
        return s and s[-1].r_att and self.l_att[-1] < s[-1].r_att[0]
            
    def combine(self, block):
        """
        Combine this block with the given block by simply concatenating all 
        lists.

        """
        self.l_att.extend(block.l_att)
        self.r_att.extend(block.r_att)
        self.l_seg.extend(block.l_seg)
        self.r_seg.extend(block.r_seg)
        
    def clean(self, dfs_num_w, alpha):
        """
        Remove the attachment w from this block (it is guaranteed to be the 
        first attachment). If the block becomes empty then record the placement 
        of all segments of the block in the array alpha and return True, False 
        otherwise. 

        """
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
        
    def add_to_att(self, att, dfs_num_w0, alpha):
        """
        Add this block to the end of the given attachment list, flipping where 
        necessary.

        First makes sure that the right side has no attachment above w0 (by 
        flipping). When add_to_Att is called at least one side has no attachment 
        above w0. add_to_att then adds the lists r_att and l_att to the output 
        list att and records the placement of all segments in the block in 
        alpha.

        """
        if self.r_att and self.r_att[0] > dfs_num_w0:
            self.flip()

        att.extend(self.l_att)
        del self.l_att[:]
        att.extend(self.r_att) 
        del self.r_att[:]

        for e in self.l_seg:
            alpha[e] = LEFT
        for e in self.r_seg:
            alpha[e] = RIGHT


class ReorderEdgesDfsIterator(object):

    """
    DFS node iterator object used to compute dfs_num, parent, lowpt1 and lowpt2, 
    for all nodes. This will also store all forward edges and all reversals of 
    tree edges that need to be deleted later.

    """

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
            if y not in self.visited:   # The edge is a tree edge.
                self.parents[y] = x
                self.visit_node(y)
                self.lowpt1s[x] = min(self.lowpt1s[x], self.lowpt1s[y])
            else:
                self.lowpt1s[x] = min(self.lowpt1s[x], self.dfs_nums[y])

                # Forward edge or reversal of tree edge.
                if self.dfs_nums[y] >= self.dfs_nums[x] or y == self.parents[x]: 
                    self.del_edges.append(edge) 

        # We know lowpt1 of x at this point and will now make a second pass over 
        # all adjacent edges of x to compute lowpt2.
        for edge in self.g.edges(x):
            y = edge[1]
            if self.parents.get(y) == x:    # Tree edge.
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

        # Store data collected on the graph itself.
        nx.set_node_attributes(self.g, self.dfs_nums, 'dfs_num')
        nx.set_node_attributes(self.g, self.parents, 'parent')
        nx.set_node_attributes(self.g, self.lowpt1s, 'lowpt1')
        nx.set_node_attributes(self.g, self.lowpt2s, 'lowpt2')


class CycleDfsIteratorBase(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, g):
        self.g = g

    def find_cycle(self, e0):
        """
        Find the cycle "C(e0)" by following first edges until a back edge is 
        encountered. Return three nodes: The cycle's first node, the last node
        on the tree path and the back edge's destination node.

        """
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

        print '        wk (last node on tree path):', wk
        print '        w0 (back edge destination):', e[1]

        return x, wk, e[1]

    @abc.abstractmethod
    def visit_edge(self, edge):
        """"""

    @abc.abstractmethod
    def run(self, source=None):
        """"""


class StronglyPlanarDfsIterator(CycleDfsIteratorBase):

    def __init__(self, *args, **kwargs):
        super(StronglyPlanarDfsIterator, self).__init__(*args, **kwargs)

        self.alpha = {}

    def visit_edge(self, edge, att):
        dfs_nums = self.g.nodes.data('dfs_num')
        parents = self.g.nodes.data('parent')
        x, w, w0 = self.find_cycle(edge)
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
                    
                # Update the stack of attachments.
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
                    
            while stack and stack[-1].clean(dfs_nums[parents[w]], self.alpha):
                stack.pop()
                
            w = parents[w]
        
        del att[:]
        while stack:
            block = stack.pop()
            if (block.l_att and block.r_att and block.l_att[0] > dfs_nums[w0] and 
                block.r_att[0] > dfs_nums[w0]):
                return False
            block.add_to_att(att, dfs_nums[w0], self.alpha)
            
        # Let's not forget that "w0" is an attachment of "S(e0)" except if 
        # w0 == x.
        if w0 != x: 
            att.append(dfs_nums[w0])

        return True

    def run(self, source=None):
        att = []
        if source is None:
            source = list(self.g.edges)[0]
        result = self.visit_edge(source, att)

        # Store data collected on the graph itself.
        nx.set_edge_attributes(self.g, LEFT, 'alpha')
        nx.set_edge_attributes(self.g, self.alpha, 'alpha')

        return result


def calculate_edge_weights(g):
    """
    Calculate the edge weight for each edge in the graph based on dfs_num, 
    lowpt1 and lowpt2 values.

    """
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


def process_biconnected_subgraph(dg):
   
    # Create an iterator that will traverse the graph in a dfs manner, 
    # calculating dfs_num, lowpt1 and lowpt2 for each node.
    itr = ReorderEdgesDfsIterator(dg)
    itr.run(source='N1')    # TO DO: Remove
    dg.remove_edges_from(itr.del_edges)

    # Sort the edges based on their lowpt1 and lowpt2 values. Use an ordered
    # graph so the order can be maintained.
    odg = nx.OrderedDiGraph()
    odg.add_nodes_from(dg.nodes(data=True))
    calculate_edge_weights(dg)
    odg.add_edges_from(sorted(dg.edges(data=True), key=lambda e: e[2]['weight']))

    # Run the stronly planar function.
    itr = StronglyPlanarDfsIterator(odg)
    print 'planar:', itr.run(('N1', 'N2'))    # TO DO: Remove
    return itr


def run(g):

    # Bail if the graph isn't connected.
    if not nx.is_connected(g):
        raise Exception('Graph not connected!')

    # Base planarity algorithm only works on biconnected components. Run the
    # algorithm on each bicon separately then combine at the end.
    for bicons in nx.biconnected_components(g):
        dg = nx.DiGraph(nx.subgraph(g, bicons))
        process_biconnected_subgraph(dg)


if __name__ == '__main__':
    g = nx.read_graphml(r'C:\Users\Jamie Davies\Documents\Graphs\test00.graphml')
    run(g)