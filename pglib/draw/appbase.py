import abc


class AppBase(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run(self):
        """"""