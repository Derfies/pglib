class Point2d(object):

    def __init__(self, x, y):
        self._data = [x, y]

    def __str__(self):
        return str(self._data)

    def __copy__(self):
        return self.__class__(*self._data)

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    def __add__(self, other):
        return self.__class__(
            self._data[0] + other._data[0],
            self._data[1] + other._data[1]
        )

    def __sub__(self, other):
        return self.__class__(
            self._data[0] - other._data[0],
            self._data[1] - other._data[1]
        )