#from collections import MutableSequence


class Point2d(object):

    def __init__(self, x, y):
        self._data = [x, y]

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] += value

    def __add__(self, other):
        return self.__class__(
            self._data[0] + other._data[0],
            self._data[1] + other._data[1]
        )