class Rect(object):

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    @property
    def width(self):
        return abs(self.p2.x - self.p1.x)

    @property
    def height(self):
        return abs(self.p2.y - self.p1.y)