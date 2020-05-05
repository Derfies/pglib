import random

import numpy as np

from regionbase import RegionBase


TILE_EMPTY = 0
TILE_CRATE = 1


class DepthFirstMaze(RegionBase):

    """
    Taken from: https://arcade.academy/examples/maze_depth_first.html
    """

    def _create_grid_with_cells(self, width, height):
        """ Create a grid with empty cells on odd row/column combinations. """
        grid = np.full((width, height), TILE_EMPTY)
        rows = grid.shape[0]
        cols = grid.shape[1]
        for row in range(rows):
            for column in range(cols):
                if column % 2 == 1 and row % 2 == 1:
                    grid[row][column] = TILE_EMPTY
                elif column == 0 or row == 0 or column == width - 1 or row == height - 1:
                    grid[row][column] = TILE_CRATE
                else:
                    grid[row][column] = TILE_CRATE
        return grid

    def make_maze_depth_first(self, maze_width, maze_height):
        maze = self._create_grid_with_cells(maze_width, maze_height)

        w = (len(maze[0]) - 1) // 2
        h = (len(maze) - 1) // 2
        vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]

        def walk(x, y):
            vis[y][x] = 1

            d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
            random.shuffle(d)
            for (xx, yy) in d:
                if vis[yy][xx]:
                    continue
                if xx == x:
                    maze[max(y, yy) * 2][x * 2 + 1] = TILE_EMPTY
                if yy == y:
                    maze[y * 2 + 1][max(x, xx) * 2] = TILE_EMPTY

                walk(xx, yy)

        walk(random.randrange(w), random.randrange(h))

        return maze

    def _run(self, region):

        # TODO: Want to embed this a little so run automatically gets called
        # with the padding region.
        #region = self.get_padding_region(region)

        region.matrix = self.make_maze_depth_first(region.width, region.height)

        return [region]