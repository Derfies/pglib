import abc


class Base(object):

    __metaclass__ = abc.ABCMeta

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    @abc.abstractmethod
    def next(self):
        """"""