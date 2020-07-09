import unittest

import networkx as nx

from pglib.graph.orthogonalface import Face


class TestFace(unittest.TestCase):

    def test_unconnected(self):
        with self.assertRaises(nx.NetworkXError) as context:
            Face([('a', 'b')])
        self.assertTrue('Input is not connected.' in context.exception)

    def test_chord(self):
        with self.assertRaises(nx.NetworkXError) as context:
            Face([('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'a'), ('a', 'c')])
        self.assertTrue('Input contains a chord.' in context.exception)


if __name__ == '__main__':
    unittest.main()