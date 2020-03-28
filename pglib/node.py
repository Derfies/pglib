import logging


logger = logging.getLogger(__name__)


class Node(object):

    def __init__(self, name, generator=None, selector=None, data=None):
        self.name = name
        self.generator = generator
        self.selector = selector
        self.data = data or []

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

        for child in self.children:
            del child.data[:]

        # Recurse through children.
        for child in self.children:
            child.clear()

    def evaluate(self):
        self.clear()

        logger.info('Evaluating: {} size: {}'.format(self.name, len(self.data)))
        if self.generator is None:
            return
        #else:

        if not self.children:
            raise Exception('Generator assigned but no children')
        # if not self.selector:
        #     raise Exception('Generator assigned but no selector')

        #for child in self.children:
        #    del child.data[:]

        for data in self.data:
            output = self.generator.run(data)

            # If no selector has been set, wrap the output in a node and call it
            # a day.
            # TODO: Be strict. Makes no sense to have a generator an no children.
            #
            # if self.selector is None or not self.children:
            #
            #     # TODO: Don't do this as the children evaluate later. It's
            #     # confusing. Also it changes the tree shape during runtime.
            #     self._children.append(Node('unnamed_{}'.format(self.name), data=output))
            #     continue

            # Otherwise select the data using the selector and add to the 
            # child's data.
            for child in self.children:
                child.data.extend(self.selector.select(child.name, output))

        # Recurse through children.
        for child in self.children:
            child.evaluate()