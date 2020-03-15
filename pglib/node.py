import logging


logger = logging.getLogger(__name__)


class Node(object):

    def __init__(self, data=None):
        self.data = data or []
        self.children = []
        self.generator = None
        self.selector = None

    def evaluate(self):
        if self.generator is None:
            #logger.warning('Leaf node found - generator not set')
            return

        for data in self.data:
            output = self.generator.run(data)

            # If no selector has been set, wrap the output in a node and call it
            # a day.
            if self.selector is None:
                self.children.append(Node(output))
                continue

            #for node in self.selector.select(output):
            ##    node.generator = self.selector.generator
            #    self.children.append(node)
            self.selector.data = output
            for prop_name, generator in self.selector.map.items():
                node = getattr(self.selector, prop_name)
                print 'node:', node, node.data
                node.generator = generator
                self.children.append(node)

        # Recurse through children.
        for child in self.children:
            child.evaluate()