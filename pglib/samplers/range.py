import random

from base import Base


class Range(Base):

    def __init__(self, *args):
        args = list(args)
        if len(args) == 1:
            args.insert(0, 0)
        self.min = args[0]
        self.max = args[1]
    
    def run(self):
        return random.randint(self.min, self.max)