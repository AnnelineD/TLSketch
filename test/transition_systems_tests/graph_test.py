import unittest
from src.transition_system.graph import DirectedGraph


class MyTestCase(unittest.TestCase):
    def test_grow(self):
        g = DirectedGraph()
        self.assertEqual(0, g.size())
        idx = g.grow()
        self.assertEqual(0, idx)
        self.assertEqual(1, g.size())

    def test_add_edge(self):
        g = DirectedGraph()
        idx1 = g.grow()
        idx2 = g.grow()
        g.add(idx1, idx2, "l")
        self.assertEqual([([1], ["l"]), ([], [])], g.adj)

        # add existing edge
        g.add(idx1, idx2, "test")
        self.assertEqual([([1], ["l"]), ([], [])], g.adj)

        # add outgoing with smaller index then other outgoings
        idx3 = g.grow()
        g.add(idx3, idx2, '32')
        g.add(idx3, idx1, '31')
        self.assertEqual([([1], ['l']), ([], []), ([0, 1], ['31', '32'])], g.adj)

        # commutative

        # out of range
        # self.assertRaises(AssertionError, g.add(4, 0, 'l'))




if __name__ == '__main__':
    unittest.main()
