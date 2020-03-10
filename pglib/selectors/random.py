import random
import logging

from base import Base


logger = logging.getLogger(__name__)


class Random(Base):

    set_names = {'A', 'B'}

    # def run(self, nodes):

       

    #     for name, gen in self.generators.items():
            

    #     # cls = self.next_generator
    #     # for node in nodes:
    #     #     obj = cls(10, 10)
    #     #     self.generators.append(obj)
    #     #     obj.input_node = Node(node)
    #     #     obj.run()