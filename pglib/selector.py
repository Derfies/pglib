class SelectorBase(object):

    def __init__(self):
        print 'init'

    def run(self):

        # Run this generator.
        output_nodes = self.generate()
        self.selector.run(output_nodes)