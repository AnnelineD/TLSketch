import unittest

from src.transition_system.tarski import *
from examples import *


class TarskiSystemTest(unittest.TestCase):
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain('blocks_4_clear/domain.pddl')
    problem = reader.parse_instance('blocks_4_clear/p-3-0.pddl')

    def test_something(self):

        st, g = construct_graph(self.problem)
        self.assertEqual(len(st), 22)
        self.assertEqual(len(st), g.size())
        for i, (n, nbs) in enumerate(g.adj):
            print(i, n)
            print(i in n)
            self.assertFalse(i in n)

        print(construct_graph(self.problem)[1].show())

    def test_gripper(self):

        domain = Gripper()
        print(domain.tarski_system().graph.adj)
        for i, (n, nbs) in enumerate(domain.tarski_system().graph.adj):  # test no self loops
            if i not in domain.tarski_system().goal_states:
                self.assertFalse(i in n)


if __name__ == '__main__':
    unittest.main()
