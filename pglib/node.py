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
        #logger.info('Evaluating node...')

        for data in self.data:
            output = self.generator.generate(data)

            if self.selector is None:
                #logger.warning('Selector not set')
                self.children.append(Node(output))
                continue

            for node in self.selector.select(output):
                node.generator = self.selector.generator
                self.children.append(node)

        for child in self.children:
            child.evaluate()