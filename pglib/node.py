import logging


logger = logging.getLogger(__name__)


class Node(object):

    def __init__(self, name, generator, selector=None):
        self.name = name
        self.generator = generator
        self.selector = selector

        self.inputs = []
        self.outputs = []
        self._children = []

    @property
    def children(self):
        return tuple(self._children[:])

    def add_child(self, child):
        if self.selector is None:
            raise ValueError('Selector not set')
        properties = self.selector.properties
        if child.name not in properties:
            props_str = map(lambda x: '"' + x + '"', properties)
            msg = 'No output named "{}" in [{}]'.format(child.name, ', '.join(props_str))
            raise ValueError(msg)
        self._children.append(child)

    def clear(self):
        del self.outputs[:]
        for child in self.children:
            del child.inputs[:]
            child.clear()

    def evaluate(self):
        logger.info('Evaluating: {} size: {}'.format(self.name, len(self.outputs)))
        self.clear()
        if self.generator is None:
            return
        for input_ in self.inputs:
            outputs = self.generator.run(input_)
            self.outputs.extend(outputs)
            for child in self.children:
                child.inputs.extend(self.selector.select(child.name, outputs))
        for child in self.children:
            child.evaluate()