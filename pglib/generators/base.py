import abc
import logging


logger = logging.getLogger(__name__)


class Base(object):

    def __init__(self, selector=None):
        self._input_node = None
        self.output_nodes = []
        self.selector = selector

    @property
    def input_node(self):
        return self._input_node

    @input_node.setter
    def input_node(self, node):
        self._input_node = node

    @abc.abstractmethod
    def generate(self):
        """Generate content here."""

    def run(self):

        logger.info('Running generator')

        # Run this generator.
        self.output_nodes = self.generate()
        if self.selector is not None:
            self.selector.run(self.output_nodes)



if __name__ == '__main__':

    from node import Node
    from region import Region

    g = GeneratorBase()
    g.input_node = Node(Region(0, 0, 1, 1))
    g.run()