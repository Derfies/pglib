import abc
import logging

from pglib.node import Node


logger = logging.getLogger(__name__)


class Base(object):

    def __init__(self, next_generator):
        self.next_generator = next_generator

        self.generators = []

    def run(self, nodes):

        # Run this selector.
        logger.info('Running selector')

        cls = self.next_generator
        for node in nodes:
            obj = cls(10, 10)
            self.generators.append(obj)
            obj.input_node = Node(node)
            obj.run()