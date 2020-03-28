from base import Base


class All(Base):

    @property
    def all(self):
        return self.data