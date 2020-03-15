import abc
import logging

from pglib.node import Node


logger = logging.getLogger(__name__)


class Base(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.parent_generator = None
        self.generators = {}

        self.generator = None

    # @abc.abstractproperty
    # def set_names(self):
    #     """"""

    #def set_generator(self, gen):
        #if name not in self.set_names:
        #    raise ValueError('{} is not a valid set name'.format(name))
        #self.generators[name] = gen

    @abc.abstractmethod
    def select(self):
        """"""

    # def run(self):

    #     logger.info('Running selector')

    #     # Run this selector.
    #     buckets = self.select()

    #     # Pass the nodes to the next generator.
    #     # TODO: Should generators take a single node or list of nodes as input?
    #     for name, nodes in buckets.items():
    #         if name not in self.generators:
    #             logger.info('Ignoring output: {}'.format(name))
    #             continue
    #         self.generators[name].input_node = Node(nodes[0])
    #         self.generators[name].run()