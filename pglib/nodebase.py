import operator


class NodeBase(object):

    def __init__(self, children=None):
        self.children = children or []

    def _recurse_callable(self, fn, *args, **kwargs):
        result = []
        stack = [self]
        done = False
        while not done:
            node = stack.pop()
            return_ = fn(node, *args, **kwargs)
            if return_ is not None:
                result.extend(return_)
            stack.extend(node.children)
            if not stack:
                done = True
        return result

    @property
    def descendents(self):
        return self._recurse_callable(operator.attrgetter('children'))

    @property
    def subtree(self):
        descendents = self.descendents
        descendents.insert(0, self)
        return descendents

    @property
    def leaves(self):
        return filter(lambda x: not x.children, self.descendents)