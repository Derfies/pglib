from base import Base


class Half(Base):

    def select(self, data):
        half_index = len(data) / 2
        return [data[:half_index], data[half_index:]]