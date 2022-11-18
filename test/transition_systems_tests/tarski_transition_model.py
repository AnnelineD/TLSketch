import unittest

from src.transition_system.tarski_transition_model import *


class MyTestCase(unittest.TestCase):
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain('../../blocks_4_clear/domain.pddl')
    problem = reader.parse_instance('../../blocks_4_clear/p-3-0.pddl')

    def test_something(self):

        st, g = tarski_transition_model(self.problem)
        self.assertEqual(len(st), 22)
        self.assertEqual(len(st), g.size())
        print(tarski_transition_model(self.problem)[1].show())


if __name__ == '__main__':
    unittest.main()
