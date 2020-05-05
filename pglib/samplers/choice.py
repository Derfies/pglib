import random

from base import Base


class Choice(Base):

    def __init__(self, items):
        self.items = items
    
    def run(self):
        return random.choice(self.items)