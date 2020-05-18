from base import Base


class Constant(Base):

    def __init__(self, value):
        self.value = value

    def next(self):
        return self.value