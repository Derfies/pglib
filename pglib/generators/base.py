import abc
import logging


logger = logging.getLogger(__name__)


class Base(object):

    """
    Notes: 

    Can a bsp tree be a dynamic tree of generator / selectors at runtime?
    """

    __metaclass__ = abc.ABCMeta

    # def __init__(self):
    #     #self._input_node = None
    #     #self._selector = None

    #     self.output_nodes = []

    # @property
    # def input_node(self):
    #     return self._input_node

    # @input_node.setter
    # def input_node(self, node):
    #     self._input_node = node

    # @property
    # def selector(self):
    #     return self._selector

    # @selector.setter
    # def selector(self, selector):
    #     selector.parent_generator = self
    #     self._selector = selector

    @abc.abstractmethod
    def generate(self):
        """Generate content here."""

    def run(self):

        logger.info('Running generator')

        # Run this generator.
        return self.generate()

        # Pass the output to the selector if one is defined.
        #if self.selector is not None:
        #    self.selector.run()



if __name__ == '__main__':

    from node import Node
    from region import Region

    g = GeneratorBase()
    g.input_node = Node(Region(0, 0, 1, 1))
    g.run()