class Base(object):

    def __init__(self, data=None):
        self.data = data or []

        self.map = {}