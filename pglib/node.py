import logging

from nodebase import NodeBase
from datanode import DataNode
from selectors.base import Base as SelectorBase


logger = logging.getLogger(__name__)


class Node(NodeBase):

    def __init__(self, name, generator, selector=None, recurse_while_fn=None,
                 children=None):
        super(Node, self).__init__(children)

        self.name = name
        self.generator = generator
        self.selector = selector
        if self.selector is None:
            self.selector = SelectorBase()
        self.recurse_while_fn = recurse_while_fn

        self.inputs = []
        self.rec_children = []

    def clear(self):
        for input_ in self.inputs:
            input_.children = []

    def add_input(self, input_):
        self.inputs.append(DataNode(input_))

    def add_child(self, node, selector=None):
        self.children.append(node)
        self.selector.connect(node, selector)

    def evaluate(self, depth=0):

        # Nuke.
        logger.info('Evaluating: {}'.format(self.name))
        self.clear()
        if self.generator is None:
            logger.info('   Node has no generator')
            return

        # Run the generator over this node's input.
        logger.info('   Using {} inputs'.format(len(self.inputs)))
        for input_ in self.inputs:
            input_.children = map(DataNode, self.generator.run(input_))
        logger.info('   Created {} outputs'.format(sum([len(i.children) for i in self.inputs])))

        if self.recurse_while_fn is not None:

            # Iterate over outputs and see if the value can be recursed.
            rec_inputs = []
            for input_ in self.inputs:
                input_children = filter(lambda x: self.recurse_while_fn(depth, x), input_.children)
                rec_inputs.extend(input_children)

            # Recurse any children if they are eligible.
            if rec_inputs:
                logger.info('   Recursing depth {}'.format(depth))
                rec_node = Node(self.name + '_' + str(depth), self.generator, recurse_while_fn=self.recurse_while_fn)
                self.rec_children.append(rec_node)
                rec_node.inputs = rec_inputs
                rec_node.evaluate(depth + 1)
            else:
                logger.info('   Recursion complete')

        # Run the selector over each set of outputs and set them as the
        # input to each child.
        # TODO: Need to select recursion result and pass to children somehow.

        for child in self.children:
            child.inputs = []

        for input_ in self.inputs:
            self.selector.input = input_
            for child in self.children:
                child.inputs.extend(self.selector.run(child))

        for child in self.children:
            child.evaluate()