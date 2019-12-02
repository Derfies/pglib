from operator import itemgetter

import networkx as nx


LEFT = 0
RIGHT = 1


class Block(object):
    # The constructor takes an edge and a list of attachments and creates 
    # a block having the edge as the only segment in its left side.
    #
    # |flip| interchanges the two sides of a block.
    #
    # |head_of_Latt| and |head_of_Ratt| return the first elements 
    # on |Latt| and |Ratt| respectively 
    # and |Latt_empty| and |Ratt_empty| check these lists for emptyness.
    #
    # |left_interlace| checks whether the block interlaces with the left 
    # side of the topmost block of stack |S|. 
    # |right_interlace| does the same for the right side.
    #
    # |combine| combines the block with another block |Bprime| by simply 
    # concatenating all lists.
    #
    # |clean| removes the attachment |w| from the block |B| (it is 
    # guaranteed to be the first attachment of |B|). 
    # If the block becomes empty then it records the placement of all 
    # segments in the block in the array |alpha| and returns true.
    # Otherwise it returns false.
    #
    # |add_to_att| first makes sure that the right side has no attachment 
    # above |w0| (by flipping); when |add_to_att| is called at least one 
    # side has no attachment above |w0|.
    # |add_to_att| then adds the lists |Ratt| and |Latt| to the output list 
    # |Att| and records the placement of all segments in the block in |alpha|.

    def __init__(self, e, A):
        # list of attachments "ints"
        self.l_att = []
        self.r_att = [] 

        # list of segments represented by their defining "edges"
        self.l_seg = []
        self.r_seg = [] 

        self.l_seg.append(e)
        self.l_att.extend(A)  # the other two lists are empty
            
    def flip(self):
        self.r_att, self.l_att = self.l_att, self.r_att
        self.r_seg, self.l_seg = self.l_seg, self.r_seg
        
    def left_interlace(self, s):
        # Check for interlacing with the left side of the topmost block of |s|
        return s and s[-1].l_att and self.l_att[-1] < s[-1].l_att[0]

    def right_interlace(self, s):
        # Check for interlacing with the right side of the topmost block of |s|
        return s and s[-1].r_att and self.l_att[-1] < s[-1].r_att[0]
            
    def combine(self, block):
        # add block to the rear of |this| block
        self.l_att.extend(block.l_att)
        self.r_att.extend(block.r_att)
        self.l_seg.extend(block.l_seg)
        self.r_seg.extend(block.r_seg)
        
    def clean(self, dfs_num_w, alpha, dfs_num):

        # remove all attachments to |w|; there may be several
        while self.l_att and self.l_att[0] == dfs_num_w:
            self.l_att.pop(0)
        while self.r_att and self.r_att[0] == dfs_num_w:
            self.r_att.pop(0)
        if self.l_att or self.r_att:
            return False
            
        # |Latt| and |Ratt| are empty;
        #  we record the placement of the subsegments in |alpha|.
        for e in self.l_seg:
            alpha[e] = LEFT

        for e in self.r_seg:
            alpha[e] = RIGHT 
            
        return True
        
    def add_to_att(self, Att, dfs_num_w0, alpha, dfs_num):

        # add the block to the rear of |Att|. Flip if necessary
        if self.r_att and self.r_att[0] > dfs_num_w0:
            #print 'add to att flip'
            self.flip()

        Att.extend(self.l_att)
        del self.l_att[:]
        Att.extend(self.r_att) 
        del self.r_att[:]

        # This needs some explanation. 
        # Note that |Ratt| is either empty or {w0}.
        # Also if |Ratt| is non-empty then all subsequent
        # sets are contained in {w0}. 
        # So we indeed compute an ordered set of attachments.
        for e in self.l_seg:
            alpha[e] = LEFT
            #print '     e:', e, 'is LEFT'
        for e in self.r_seg:
            alpha[e] = RIGHT
            #print '     e:', e, 'is RIGHT'


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
        print x, '->', self.dfs_num
        self.dfs_nums[x] = self.dfs_num
        self.lowpt1s[x] = self.lowpt2s[x] = self.dfs_num
        self.visited.add(x)
        self.dfs_num += 1

        # Calculate low point 1.
        edges = list(self.g.edges(x))
        edges.sort(key=lambda x: (len(x[1]), x[1]))
        #print x, '->', edges
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
            source = list(self.g)[0]
        self.visit_node(source)


def calculate_edge_weights(g, dfs_nums, lowpt1s, lowpt2s):
    weights = {}
    for edge in g.edges:
        x, y = edge
        if dfs_nums[y] < dfs_nums[x]:
            weights[edge] = 2 * dfs_nums[y]
        elif lowpt2s[y] >= dfs_nums[x]:
            weights[edge] = 2 * lowpt1s[y]
        else:
            weights[edge] = 2 * lowpt1s[y] + 1
    return weights


def sort_edges(weights):
    edges = weights.items()
    edges.sort(key=lambda x: x[1])
    return map(itemgetter(0), edges)


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

                # TEST RECURSIVELY
                # Let "e" be any edge leaving the spine. 
                # We need to test whether "S(e)" is strongly planar 
                # and if so compute its list |A| of attachments.
                # If "e" is a tree edge we call our procedure recursively 
                # and if "e" is a back edge then "S(e)" is certainly strongly 
                # planar and |target(e)| is the only attachment.
                # If we detect non-planarity we return false and free
                # the storage allocated for the blocks of stack |S|.
                a = []
                if dfs_nums[w] < dfs_nums[e[1]]: 
                    if not self.visit_edge(e, a):
                        return False                    
                else:
                    a.append(dfs_nums[e[1]]) # a back edge
                    
                # UPDATE STACK |S| OF ATTACHMENTS
                # The list |A| contains the ordered list of attachments 
                # of segment "S(e)". 
                # We create an new block consisting only of segment "S(e)" 
                # (in its L-part) and then combine this block with the 
                # topmost block of stack |S| as long as there is interlacing. 
                # We check for interlacing with the L-part. 
                # If there is interlacing then we flip the two sides of the 
                # topmost block. 
                # If there is still interlacing with the left side then the 
                # interlacing graph is non-bipartite and we declare the graph 
                # non-planar (and also free the storage allocated for the
                # blocks).
                # Otherwise we check for interlacing with the R-part. 
                # If there is interlacing then we combine |B| with the topmost
                # block and repeat the process with the new topmost block.
                # If there is no interlacing then we push block |B| onto |S|.
                block = Block(e, a)
                print '        ### new block {}:'.format(i), e, a
                
                while True:
                    if block.left_interlace(stack): 
                        print '        left interlace flip'
                        stack[-1].flip()
                    if block.left_interlace(stack): 
                        return False
                    if block.right_interlace(stack): 
                        print '        right interlace combine'
                        block.combine(stack.pop())
                    else: 
                        break

                stack.append(block)
                    
            # PREPARE FOR NEXT ITERATION
            # We have now processed all edges emanating from vertex |w|. 
            # Before starting to process edges emanating from vertex
            # |parent[w]| we remove |parent[w]| from the list of attachments
            # of the topmost 
            # block of stack |S|. 
            # If this block becomes empty then we pop it from the stack and 
            # record the placement for all segments in the block in array
            # |alpha|.
            while stack and stack[-1].clean(dfs_nums[dfs_parents[w]], self.alpha, dfs_nums):
                stack.pop()
                
            w = dfs_parents[w]
            
        # TEST STRONG PLANARITY AND COMPUTE Att
        # We test the strong planarity of the segment "S(e0)". 
        # We know at this point that the interlacing graph is bipartite. 
        # Also for each of its connected components the corresponding block 
        # on stack |S| contains the list of attachments below |x|. 
        # Let |B| be the topmost block of |S|. 
        # If both sides of |B| have an attachment above |w0| then 
        # "S(e0)" is not strongly planar. 
        # We free the storage allocated for the blocks and return false.
        # Otherwise (cf. procedure |add_to_att|) we first make sure that 
        # the right side of |B| attaches only to |w0| (if at all) and then 
        # add the two sides of |B| to the output list |Att|.
        # We also record the placements of the subsegments in |alpha|.
        del att[:]
        while stack:
            block = stack.pop()
            if block.l_att and block.r_att and block.l_att[0] > dfs_nums[w0] and block.r_att[0] > dfs_nums[w0]:
                return False
            block.add_to_att(att, dfs_nums[w0], self.alpha, dfs_nums)
            
        # Let's not forget that "w0" is an attachment of "S(e0)" except if w0 = x.
        if w0 != x: 
            att.append(dfs_nums[w0])

        print 'strongly_planar DONE:', edge, att#.elements#, [dfs_numtovert[el] for el in Att.elements]
        print 'alpha:', self.alpha
        print ''
        
        return True

    def run(self, source=None):
        att = []
        if source is None:
            source = list(self.edges)[0]
        self.visit_edge(source, att)
        return att


def strongly_planar(g, e0, dfs_nums, parents, att, alpha):

    print 'strongly_planar:', e0

    #print 'dfs_nums:', dfs_nums
  
    # We now come to the heart of the planarity test: procedure strongly_planar.
    # It takes a tree edge e0=(x,y) and tests whether the segment S(e0) is 
    # strongly planar. 
    # If successful it returns (in Att) the ordered list of attachments of S(e0) 
    # (excluding x); high DFS-numbers are at the front of the list.
    # In alpha it records the placement of the subsegments.
    
    # strongly_planar operates in three phases.
    # It first constructs the cycle C(e0) underlying the segment S(e0). 
    # It then constructs the interlacing graph for the segments emanating >from the
    # spine of the cycle.
    # If this graph is non-bipartite then the segment S(e0) is non-planar.
    # If it is bipartite then the segment is planar.
    # In this case the third phase checks whether the segment is strongly planar 
    # and, if so, computes its list of attachments.

    #global G, alpha, dfs_num, parent

    # DETERMINE THE CYCLE C(e0)
    # We determine the cycle "C(e0)" by following first edges until a back 
    # edge is encountered. 
    # |wk| will be the last node on the tree path and |w0|
    # is the destination of the back edge.
    #x = source(e0)
    #y = target(e0)
    x, y = e0
    e = list(g.edges(y))[0]
    wk = y
    
    print '    cycle:'
    print '        e0:', e0
    print '        e: ', e
    while dfs_nums[e[1]] > dfs_nums[wk]:  # e is a tree edge
        wk = e[1]
        e = list(g.edges(wk))[0]
        print '        e: ', e
    w0 = e[1]
    print '        wk (last node on tree path):', wk
    print '        w0 (back edge destination):', w0

    # PROCESS ALL EDGES LEAVING THE SPINE
    # The second phase of |strongly_planar| constructs the connected 
    # components of the interlacing graph of the segments emananating 
    # from the the spine of the cycle "C(e0)". 
    # We call a connected component a "block". 
    # For each block we store the segments comprising its left and 
    # right side (lists |Lseg| and |Rseg| contain the edges defining 
    # these segments) and the ordered list of attachments of the segments
    # in the block; 
    # lists |Latt| and |Ratt| contain the DFS-numbers of the attachments; 
    # high DFS-numbers are at the front of the list. 
    #
    # We process the edges leaving the spine of "S(e0)" starting at 
    # node |wk| and working backwards. 
    # The interlacing graph of the segments emanating from
    # the cycle is represented as a stack |S| of blocks.

    #'''
    print ''
    print '    segment:'

    w = wk
    #print 'w:', w
    stack = []
    
    while w != x:
        #count = 0
        for e_idx, e in enumerate(list(g.edges(w))):

            # no action for first edge
            if e_idx == 0:
                continue

            #print '    e_idx:', e_idx
            #count = count + 1
            #if count > 0: 
            # TEST RECURSIVELY
            # Let "e" be any edge leaving the spine. 
            # We need to test whether "S(e)" is strongly planar 
            # and if so compute its list |A| of attachments.
            # If "e" is a tree edge we call our procedure recursively 
            # and if "e" is a back edge then "S(e)" is certainly strongly 
            # planar and |target(e)| is the only attachment.
            # If we detect non-planarity we return false and free
            # the storage allocated for the blocks of stack |S|.
            a = []
            #print 'dfsnum[w]:', dfs_nums[w]
            #print 'dfsnum[target(e)]:', dfs_nums[e[1]]
            if dfs_nums[w] < dfs_nums[e[1]]: 
                #print 'RECURSE'
                # tree edge
                if not strongly_planar(g, e, dfs_nums, parents, a, alpha):   #g, e0, dfs_nums, parents, att
                    #while S.IsNotEmpty(): 
                    #    S.Pop()
                    return False                    
            else:
                a.append(dfs_nums[e[1]]) # a back edge
                
            # UPDATE STACK |S| OF ATTACHMENTS
            # The list |A| contains the ordered list of attachments 
            # of segment "S(e)". 
            # We create an new block consisting only of segment "S(e)" 
            # (in its L-part) and then combine this block with the 
            # topmost block of stack |S| as long as there is interlacing. 
            # We check for interlacing with the L-part. 
            # If there is interlacing then we flip the two sides of the 
            # topmost block. 
            # If there is still interlacing with the left side then the 
            # interlacing graph is non-bipartite and we declare the graph 
            # non-planar (and also free the storage allocated for the
            # blocks).
            # Otherwise we check for interlacing with the R-part. 
            # If there is interlacing then we combine |B| with the topmost
            # block and repeat the process with the new topmost block.
            # If there is no interlacing then we push block |B| onto |S|.
            block = Block(e, a)
            print '        ### new block {}:'.format(e_idx), e, a#.elements 
            #print 'BLOCK:', e, A.elements
            
            while True:
                if block.left_interlace(stack): 
                    print '        left interlace flip'
                    stack[-1].flip()
                if block.left_interlace(stack): 
                    return False
                if block.right_interlace(stack): 
                    print '        right interlace combine'
                    block.combine(stack.pop())
                else: 
                    break

            stack.append(block)
                
        # PREPARE FOR NEXT ITERATION
        # We have now processed all edges emanating from vertex |w|. 
        # Before starting to process edges emanating from vertex
        # |parent[w]| we remove |parent[w]| from the list of attachments
        # of the topmost 
        # block of stack |S|. 
        # If this block becomes empty then we pop it from the stack and 
        # record the placement for all segments in the block in array
        # |alpha|.
        while stack and stack[-1].clean(dfs_nums[parents[w]], alpha, dfs_nums):
            stack.pop()
            
        w = parents[w]
        
        
    # TEST STRONG PLANARITY AND COMPUTE Att
    # We test the strong planarity of the segment "S(e0)". 
    # We know at this point that the interlacing graph is bipartite. 
    # Also for each of its connected components the corresponding block 
    # on stack |S| contains the list of attachments below |x|. 
    # Let |B| be the topmost block of |S|. 
    # If both sides of |B| have an attachment above |w0| then 
    # "S(e0)" is not strongly planar. 
    # We free the storage allocated for the blocks and return false.
    # Otherwise (cf. procedure |add_to_att|) we first make sure that 
    # the right side of |B| attaches only to |w0| (if at all) and then 
    # add the two sides of |B| to the output list |Att|.
    # We also record the placements of the subsegments in |alpha|.
    del att[:]
    while stack:
        B = stack.pop()
        if (B.l_att and B.r_att and
            B.l_att[0] > dfs_nums[w0] and B.r_att[0] > dfs_nums[w0]):
            #del B
            #while S.IsNotEmpty(): 
            #    S.Pop()
            return False
        B.add_to_att(att, dfs_nums[w0], alpha, dfs_nums)
        del B
        
    # Let's not forget that "w0" is an attachment of "S(e0)" except if w0 = x.
    if w0 != x: 
        att.append(dfs_nums[w0])



    print 'strongly_planar DONE:', e0, att#.elements#, [dfs_numtovert[el] for el in Att.elements]
    print 'alpha:', alpha
    print ''
    
    return True
    #'''


def process_biconnected_subgraph(g):
   
    # Create an iterator that will traverse the graph in a dfs manner, 
    # calculating dfs_num, lowpt1 and lowpt2 for each node.
    itr = ReorderEdgesDfsIterator(g)
    itr.run(source='N1')
    g.remove_edges_from(itr.del_edges)

    # Calculate edges weights and sort.
    weights = calculate_edge_weights(g, itr.dfs_nums, itr.lowpt1s, itr.lowpt2s)

    print 'lowpt1s'
    for k  in sorted(itr.lowpt1s):
        print k, '->', itr.lowpt1s[k]
    print '--lowpt1s--'

    print 'lowpt2s'
    for k  in sorted(itr.lowpt2s):
        print k, '->', itr.lowpt2s[k]
    print '--lowpt2s--'

    edges = sort_edges(weights)
    print 'weights'
    for k  in sorted(weights):
        print k, '->', weights[k]
    print '--weights--'
   
    # Create a new ordered graph to represent the sorted edges.
    og = nx.OrderedDiGraph()
    og.add_nodes_from(g.nodes)
    og.add_edges_from(edges)

    # Encode dfs_num and dfs_parent onto each node.
    nx.set_node_attributes(og, itr.dfs_nums, 'dfs_num')
    nx.set_node_attributes(og, itr.parents, 'dfs_parent')


    attr = []
    first_edge = ('N1', 'N2')#list(og.edges)[0]
    alpha = {first_edge: LEFT}


    print 'verts:', g.nodes
    print 'edges:', g.edges
    #print 'adjEdges:', G.adjEdges
    print ''

    #print 'first node:', g.nodes
    #print 'first first_adj_edge:', list(og.edges)[0]
    #print ''


    result = strongly_planar(og, first_edge, itr.dfs_nums, itr.parents, attr, alpha)
    print 'result:', result

    print 'attr:', attr
    print 'alpha:', alpha

    print '*********************************************'
    print '*********************************************'
    print '*********************************************'

    itr = StronglyPlanarDfsIterator(og)
    itr.run(('N1', 'N2'))

    return


def run(g):

    # Bail if the graph isn't connected.
    if not nx.is_connected(g):
        raise Exception('Graph not connected!')

    # Base planarity algorithm only works on biconnected components. We'll run 
    # the algorithm on each bicon separately then combine at the end.
    for bicons in nx.biconnected_components(g):
        sg = nx.DiGraph(nx.subgraph(g, bicons))
        process_biconnected_subgraph(sg)


if __name__ == '__main__':
    g = nx.read_graphml(r'C:\Users\Jamie Davies\Documents\Graphs\test8.graphml')
    run(g)