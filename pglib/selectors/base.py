import enum


class SelectionMode(enum.Enum):

    LEAVES = 0
    DESCENDENTS = 1
    SUBTREE = 2


class Base(object):

    def __init__(self, mode=SelectionMode.LEAVES):
        self._map = {}
        self.input = None
        self.mode = mode

    def connect(self, node, selector):
        self._map[node] = selector

    def run(self, node):

        if self.mode == SelectionMode.LEAVES:
            selection = self.input.leaves
        elif self.mode == SelectionMode.DESCENDENTS:
            selection = self.input.descendents
        else:
            selection = self.input.subtree

        selector = self._map.get(node)
        if selector is None:
            return selection
        else:
            return selector(selection)