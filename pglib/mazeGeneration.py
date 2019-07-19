import random

from region import Region


NORTH = (0, -1)
SOUTH = (0, 1)
EAST = (1, 0)
WEST = (-1, 0)


def carve(region, x, y):
    region.matrix[x][y] = 0
    region.matrix[x][y] = 0


def can_carve(region, pos, dir):
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


def maze_generation(p_region, winding_percent=0.1):

    cells = []
    last_direction = None

    #start = (random.randint(0, p_region.width), random.randint(0, p_region.height))
    start = (1, 1)
    carve(p_region, start[0], start[1])

    cells.append(start)

    while cells:
        cell = cells[-1]

        # See if any adjacent cells are open.
        unmade_cells = set()
        for direction in [NORTH, SOUTH, EAST, WEST]:
            if can_carve(p_region, cell, direction):
                unmade_cells.add(direction)

        if unmade_cells:
            
            # Prefer to carve in the same direction, when
            # it isn't necessary to do otherwise.
            if last_direction in unmade_cells and random.random() > winding_percent:
                direction = last_direction
            else:
                direction = unmade_cells.pop()

            new_cell = (cell[0] + direction[0], cell[1] + direction[1])
            carve(p_region, new_cell[0], new_cell[1])

            new_cell = (cell[0] + direction[0] * 2, cell[1] + direction[1] * 2)
            carve(p_region, new_cell[0], new_cell[1])
            cells.append(new_cell)

            last_direction = direction

        else:

            # No adjacent uncarved cells
            cells.pop()
            last_direction = None