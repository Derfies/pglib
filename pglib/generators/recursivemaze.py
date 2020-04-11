import random

import numpy as np

from box import Box


TILE_EMPTY = 0
TILE_CRATE = 1


class RecursiveMaze(Box):

    def create_empty_grid(self, width, height, default_value=TILE_EMPTY):
        """ Create an empty grid. """
        return np.full((width, height), TILE_EMPTY)

    def create_outside_walls(self, maze):
        """ Create outside border walls."""

        # Create left and right walls
        for row in range(len(maze)):
            maze[row][0] = TILE_CRATE
            maze[row][len(maze[row]) - 1] = TILE_CRATE

        # Create top and bottom walls
        for column in range(1, len(maze[0]) - 1):
            maze[0][column] = TILE_CRATE
            maze[len(maze) - 1][column] = TILE_CRATE

    def make_maze_recursive_call(self, maze, top, bottom, left, right):
        """
        Recursive function to divide up the maze in four sections
        and create three gaps.
        Walls can only go on even numbered rows/columns.
        Gaps can only go on odd numbered rows/columns.
        Maze must have an ODD number of rows and columns.
        """

        # Figure out where to divide horizontally
        start_range = bottom + 2
        end_range = top - 1
        y = random.randrange(start_range, end_range, 2)

        # Do the division
        for column in range(left + 1, right):
            maze[column][y] = TILE_CRATE

        # Figure out where to divide vertically
        start_range = left + 2
        end_range = right - 1
        x = random.randrange(start_range, end_range, 2)

        # Do the division
        for row in range(bottom + 1, top):
            maze[x][row] = TILE_CRATE

        # Now we'll make a gap on 3 of the 4 walls.
        # Figure out which wall does NOT get a gap.
        wall = random.randrange(4)
        if wall != 0:
            gap = random.randrange(left + 1, x, 2)
            maze[gap][y] = TILE_EMPTY

        if wall != 1:
            gap = random.randrange(x + 1, right, 2)
            maze[gap][y] = TILE_EMPTY

        if wall != 2:
            gap = random.randrange(bottom + 1, y, 2)
            maze[x][gap] = TILE_EMPTY

        if wall != 3:
            gap = random.randrange(y + 1, top, 2)
            maze[x][gap] = TILE_EMPTY

        # If there's enough space, to a recursive call.
        if top > y + 3 and x > left + 3:
            self.make_maze_recursive_call(maze, top, y, left, x)

        if top > y + 3 and x + 3 < right:
            self.make_maze_recursive_call(maze, top, y, x, right)

        if bottom + 3 < y and x + 3 < right:
            self.make_maze_recursive_call(maze, y, bottom, x, right)

        if bottom + 3 < y and x > left + 3:
            self.make_maze_recursive_call(maze, y, bottom, left, x)

    def make_maze_recursion(self, maze_width, maze_height):
        """ Make the maze by recursively splitting it into four rooms. """
        maze = self.create_empty_grid(maze_width, maze_height)
        # Fill in the outside walls
        self.create_outside_walls(maze)

        # Start the recursive process
        self.make_maze_recursive_call(maze, maze_height - 1, 0, 0, maze_width - 1)
        return maze

    def run(self, region):

        """
        Taken from: https://arcade.academy/examples/maze_recursive.html
        """

        # TODO: Want to embed this a little so run automatically gets called
        # with the padding region.
        region = self.get_padding_region(region)

        region.matrix = self.make_maze_recursion(region.width, region.height)

        return [region]