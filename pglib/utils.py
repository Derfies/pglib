import bisect
import random

from const import *


def get_random_colour(a=0.25):
    r = random.uniform(0.0, 1.0)
    g = random.uniform(0.0, 1.0)
    b = random.uniform(0.0, 1.0)
    return r, g, b, a


def get_random_direction(directions=None):
    directions = directions or DIRECTIONS
    idx = random.randint(0, len(directions) - 1)
    return directions[idx]


def get_weighted_choice(choices):
    values, weights = zip(*choices)
    total = 0
    cum_weights = []
    for weight in weights:
        total += weight
        cum_weights.append(total)
    x = random.random() * total
    i = bisect.bisect(cum_weights, x)
    return values[i]