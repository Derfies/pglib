import abc


class Base(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run(self):
        """"""