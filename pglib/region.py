import random

import numpy as np

from const import *
from geometry import Point2d


class Region( object ):

    def __init__( self, x1, y1, x2, y2, value=0 ):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        # TO DO:
        # Turn above attributes into properties also so we can resize the matrix
        # where necessary.
        self.matrix = np.full( (self.width, self.height), value )
        self.leftChild = None
        self.rightChild = None

    def __eq__( self, other ):
        return (
            self.x1 == other.x1 and 
            self.y1 == other.y1 and
            self.y2 == other.y2 and
            self.y2 == other.y2
        )

    def __hash__( self ):
        return hash( (self.x1, self.y1, self.x2, self.y2) )

    def __copy__( self ):
        return self.__class__( self.x1, self.y1, self.x2, self.y2 )

    def __str__( self ):
       return str( self.x1 ) + ', ' + str( self.y1 ) + ', ' + str( self.x2 ) + ', ' + str( self.y2 )

    @property
    def width( self ):
        return self.x2 - self.x1

    @property
    def height( self ):
        return self.y2 - self.y1

    @property
    def centre( self ):
        x = (self.x1 + self.x2) / 2
        y = (self.y1 + self.y2) / 2
        return Point2D( x, y )

    def get2dArray( self ):
        return [
            [self.x1, self.y1], 
            [self.x2, self.y2]
        ]

    def getXEdges( self ):
        return [self.x1, self.x2]

    def getYEdges( self ):
        return [self.y1, self.y2]

    def intersects( self, other ):
        return (
            self.x1 < other.x2 and 
            self.x2 > other.x1 and
            self.y1 < other.y2 and 
            self.y2 > other.y1
        )

    def touches( self, other ):
        if isinstance( other, self.__class__ ):
            return ( 
                self.x1 <= other.x2 and 
                self.x2 >= other.x1 and
                self.y1 <= other.y2 and 
                self.y2 >= other.y1
            )
        else:
            return (
                self.x1 <= other.x and 
                self.x2 >= other.x and
                self.y1 <= other.y and
                self.y2 >= other.y
            )

    def encloses( self, other ):
        return ( 
            self.x1 <= other.x1 and 
            self.x2 >= other.x2 and
            self.y1 <= other.y1 and
            self.y2 >= other.y2
        )

    def inflate( self, d ):
        self.x1 -= d
        self.y1 -= d 
        self.x2 += d 
        self.y2 += d

    def split( self, minLeafSize ):

        # Begin splitting the leaf into two children
        if self.leftChild is not None or self.rightChild is not None:
            return False # we're already split! Abort!

        # determine direction of split
        # if the width is >25% larger than height, we split vertically
        # if the height is >25% larger than the width, we split horizontally
        # otherwise we split randomly
        splitH = random.uniform( 0, 1 ) > 0.5
        if self.width > self.height and self.width / self.height >= 1.25:
            splitH = False
        elif self.height > self.width and self.height / self.width >= 1.25:
            splitH = True

        maxD = (self.height if splitH else self.width) - minLeafSize # determine the maximum height or width
        if maxD <= minLeafSize:
            return False # the area is too small to split any more...

        split = random.randint( minLeafSize, maxD ) # determine where we're going to split

        # Create our left and right children based on the direction of the split
        if splitH:
            self.leftChild = Region( self.x1, self.y1, self.x2, self.y1 + split )
            self.rightChild = Region( self.x1, self.y1 + split, self.x2, self.y2 )
        else:
            self.leftChild = Region( self.x1, self.y1, self.x1 + split, self.y2 )
            self.rightChild = Region( self.x1 + split, self.y1, self.x2, self.y2 )

        return True # split successful!

    def blit( self, src ):
        #if loc is None:
        #    loc = (0, 0)
        loc = (src.x1, src.y1)
        src = src.matrix
        pos = [i if i >= 0 else None for i in loc]
        neg = [-i if i < 0 else None for i in loc]
        target = self.matrix[[slice(i,None) for i in pos]]
        src = src[[slice(i, j) for i,j in zip(neg, target.shape)]]
        target[[slice(None, i) for i in src.shape]] = src
        #return dest

    # A function to check if a given cell 
    # (row, col) can be included in DFS
    def isSafe( self, index, visited ):
        i, j = index
        # row number is in range, column number
        # is in range and value is 1 
        # and not yet visited
        print index
        try:
            return (i >= 0 and i < self.matrix.shape[0] and
                    j >= 0 and j < self.matrix.shape[1] and
                    not visited[index] and self.matrix[index])
        except RuntimeError:
            print 'BROKEN:', index
            raise
 
    # A utility function to do DFS for a 2D 
    # boolean matrix. It only considers
    # the 8 neighbours as adjacent vertices
    def DFS( self, index, visited, island ):
 
        # These arrays are used to get row and column numbers of 4 neighbours of
        # a given cell
        rowNbr = [-1, 0,  0, 1]
        colNbr = [ 0, -1, 1, 0]
         
        # Mark this cell as visited
        visited[index] = True
        island[index] = 2
 
        # Recurse for all connected neighbours.
        i, j = index
        for k in range( 4 ):
            if self.isSafe( (i + rowNbr[k], j + colNbr[k]), visited ):
                self.DFS( (i + rowNbr[k], j + colNbr[k]), visited, island )
 
 
    # The main function that returns
    # count of islands in a given boolean
    # 2D matrix
    def countIslands( self ):

        # Make a bool array to mark visited cells. Initially all cells are 
        # unvisited.
        visited = np.full( self.matrix.shape, False )
 
        # Initialize count as 0 and travese through the all cells of given 
        # matrix.
        self.islands = []
        for index, x in np.ndenumerate( self.matrix ):

            # If a cell with value 1 is not visited yet, then new island found.
            if visited[index] == False and self.matrix[index] == 1:
                island = np.zeros( self.matrix.shape )
                self.islands.append( island )

                # Visit all cells in this island and increment island count.
                self.DFS( index, visited, island )
 
        return self.islands

    def getRemainingArea( self, region, direction ):
        """
        Return a rect describing the area adjacent to the given region in the 
        given direction.
        """
        area = Region( self.x1, self.y1, self.x2, self.y2 )
        if direction == NEG_X:
            area.x2 = region.x1
        elif direction == NEG_Y:
            area.y2 = region.y1
        elif direction == POS_X:
            area.x1 = region.x2
        elif direction == POS_Y:
            area.y1 = region.y2
        return area