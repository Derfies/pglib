class Base(object):

    def _run(self, data):
        return [data]

    def run(self, input_):
        return self._run(input_.data)