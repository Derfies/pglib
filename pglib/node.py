import logging


logger = logging.getLogger(__name__)


class Node(object):

    def __init__(self, name, generator, selector=None, recurse_while_fn=None):
        self.name = name
        self.generator = generator
        self.selector = selector
        self.recurse_while_fn = recurse_while_fn

        self.inputs = []
        self.outputs = []
        self._children = []

    @property
    def children(self):
        return tuple(self._children[:])

    def add_child(self, child):
        self._children.append(child)

    def clear(self):
        del self.outputs[:]
        for child in self.children:
            del child.inputs[:]
            child.clear()

    def _evaluate(self, i, inputs):

        # TODO: Needs another class?
        for input_ in inputs:

            # Run this generator and add result to outputs.
            outputs = self.generator.run(input_)
            self.outputs.extend(outputs)

            # Run the selector over each set of outputs and set them as the
            # input to each child.
            for child in self.children:
                subset = outputs
                if self.selector is not None:
                    subset = self.selector.select(child.name, outputs)
                child.inputs.extend(subset)

            # If a recursion terminator function is defined use it to filter the
            # outputs in order to recurse. Those outputs that cannot be recursed
            # are leaves.
            if self.recurse_while_fn is not None:
                can_recurse = []
                cant_recurse = []
                for output in outputs:
                    if self.recurse_while_fn(i, output):
                        can_recurse.append(output)
                    else:
                        cant_recurse.append(output)
                self._evaluate(i + 1, can_recurse)

    def evaluate(self):
        #logger.info('Evaluating: {} size: {}'.format(self.name, len(self.outputs)))
        self.clear()
        if self.generator is None:
            return

        self._evaluate(0, self.inputs)

        for child in self.children:
            child.evaluate()