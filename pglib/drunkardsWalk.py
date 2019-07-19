import random

import utils
from const import *


def drunkards_walk(p_region, max_iters=25000, step_length=1, weight_to_prev_direction=0.7):

    """
    Stolen with thanks: https://github.com/AtTheMatinee/dungeon-generation
    """

    _num_filled = 0
    _prev_direction = None

    filled_goal = p_region.width * p_region.height * 0.4
    weight_to_center = 0.15

    x = random.randint(2, p_region.width - 2)
    y = random.randint(2, p_region.height - 2)

    for i in xrange(max_iters):

        dir_weights = dict.fromkeys([POS_Y, NEG_Y, POS_X, NEG_X], 1.0)

        # Weight the random walk away from the edges.
        if x < p_region.width * 0.25:        # Drunkard is at far left side of map.
            dir_weights[POS_X] += weight_to_center
        elif x > p_region.width * 0.75:      # Drunkard is at far right side of map.
            dir_weights[NEG_X] += weight_to_center
        if y < p_region.height * 0.25:       # Drunkard is at the top of the map.
            dir_weights[NEG_Y] += weight_to_center
        elif y > p_region.height * 0.75:     # Drunkard is at the bottom of the map.
            dir_weights[POS_Y] += weight_to_center

        # Weight the random walk in favor of the previous direction.
        if _prev_direction in dir_weights:
            dir_weights[_prev_direction] += weight_to_prev_direction

        # Randomise a direction and a step length.
        direction = utils.get_weighted_choice(dir_weights.items())
        step = random.randint(0, step_length)

        # Mark each cell that makes up the step.
        dx, dy = direction.dx, direction.dy
        for i in range(step):
            if 0 < x + dx < p_region.width - 1 and 0 < y + dy < p_region.height - 1:
                x += dx
                y += dy
                if p_region.matrix[x][y] == 1:
                    p_region.matrix[x][y] = 0
                    _num_filled += 1
        _prev_direction = direction

        if _num_filled >= filled_goal:
            break