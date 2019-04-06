import random

from region import Region


NORTH = (0, -1)
SOUTH = (0, 1)
EAST = (1, 0)
WEST = (-1, 0)


def carve( region, x, y ):
    region.matrix[x][y] = 0
    region.matrix[x][y] = 0


def canCarve( region, pos, dir ):
    '''
    gets whether an opening can be carved at the location
    adjacent to the cell at (pos) in the (dir) direction.
    returns False if the location is out of bounds or if the cell
    is already open.
    '''
    x = pos[0] + dir[0] * 3
    y = pos[1] + dir[1] * 3

    if not (0 < x < region.width) or not (0 < y < region.height):
        return False

    x = pos[0] + dir[0] * 2
    y = pos[1] + dir[1] * 2

    # return True if the cell is a wall (1)
    # false if the cell is a floor (0)
    return region.matrix[x][y] != 0


def mazeGeneration( pRegion, windingPercent=0.1 ):

    cells = []
    lastDirection = None

    #start = (random.randint( 0, pRegion.width ), random.randint( 0, pRegion.height ) )
    start = (1, 1)
    carve( pRegion, start[0], start[1] )

    cells.append( start )

    while cells:
        cell = cells[-1]

        # See if any adjacent cells are open.
        unmadeCells = set()
        for direction in [NORTH, SOUTH, EAST, WEST]:
            if canCarve( pRegion, cell, direction ):
                unmadeCells.add( direction )

        if unmadeCells:
            
            # Prefer to carve in the same direction, when
            # it isn't necessary to do otherwise.
            if lastDirection in unmadeCells and random.random() > windingPercent:
                direction = lastDirection
            else:
                direction = unmadeCells.pop()

            newCell = (cell[0] + direction[0], cell[1] + direction[1])
            carve( pRegion, newCell[0], newCell[1] )

            newCell = (cell[0] + direction[0] * 2, cell[1] + direction[1] * 2 )
            carve( pRegion, newCell[0], newCell[1] )
            cells.append( newCell )

            lastDirection = direction

        else:

            # No adjacent uncarved cells
            cells.pop()
            lastDirection = None