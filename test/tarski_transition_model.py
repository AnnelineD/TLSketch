import unittest

from src.transition_system.tarski_transition_model import *


class MyTestCase(unittest.TestCase):
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain('../blocks_4_clear/domain.pddl')
    problem = reader.parse_instance('../blocks_4_clear/p-3-0.pddl')

    def test_something(self):
        self.assertEqual(len(tarski_transition_model(self.problem)), 22)


if __name__ == '__main__':
    unittest.main()
