import inspect
from operator import itemgetter 


class Base(object):

    def __init__(self):
        self._map = {}
        self.input = None

    def connect(self, node, selector):
        self._map[node] = selector

    #def set_input(self, input_):
    #    self.input = input_

    def run(self, node):

        # Test - return leaf nodes only.
        selection = self.input.leaves
        selector = self._map.get(node)
        if selector is None:
            return selection
        else:
            return selector(selection)