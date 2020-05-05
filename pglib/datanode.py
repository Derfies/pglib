import logging

from nodebase import NodeBase


logger = logging.getLogger(__name__)


class DataNode(NodeBase):

    def __init__(self, data):
        super(DataNode, self).__init__()

        self.data = data