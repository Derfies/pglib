import random
import logging

from base import Base


logger = logging.getLogger(__name__)


class Chunk(Base):

    def __init__(self, num_chunks):
        super(Chunk, self).__init__()

        self.num_chunks = num_chunks

    @property
    def set_names(self):
        return map(str, range(self.num_chunks))

    def _chunk(self, list_, size):
        return [list_[i::size] for i in xrange(size)]

    def select(self):
        nodes = self.parent_generator.output_nodes
        chunks = self._chunk(nodes, self.num_chunks)
        return {
            str(i): chunk
            for i, chunk in enumerate(chunks)
        }