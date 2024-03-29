import unittest

from src.transition_system.tarski import *
from examples import *


class TarskiSystemTest(unittest.TestCase):
    path = "../../domains/"

    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain(path + 'blocks_4_clear/domain.pddl')
    problem = reader.parse_instance(path + 'blocks_4_clear/p-3-0.pddl')

    def test_something(self):
        graph_sys = construct_graph(self.problem)
        st = graph_sys.states
        g = graph_sys.graph
        self.assertEqual(len(st), 22)
        self.assertEqual(len(st), g.size())
        for i, (n, nbs) in enumerate(g.adj):
            # print(i, n)
            # print(i in n)
            self.assertFalse(i in n)

        # print(construct_graph(self.problem)[1].show())

    def test_gripper(self):

        domain = Gripper()
        # print(domain.transition_system.graph.adj)
        for i, (n, nbs) in enumerate(domain.transition_system.graph.adj):  # test no self loops
            if i not in domain.transition_system.goals:
                self.assertFalse(i in n)


if __name__ == '__main__':
    unittest.main()
