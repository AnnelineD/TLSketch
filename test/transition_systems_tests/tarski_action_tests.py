import unittest

from tarski.io import PDDLReader

from src.transition_system.tarski_manipulation import *


class MyTestCase(unittest.TestCase):
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain('../../blocks_4_clear/domain.pddl')
    problem = reader.parse_instance('../../blocks_4_clear/p-3-0.pddl')

    b1 = problem.language.get("b1")
    b2 = problem.language.get("b2")
    b3 = problem.language.get("b3")

    def test_group_constants(self):
        self.assertEqual(sort_constants(self.problem.language),
                         {self.problem.language.get("object"): [self.b1, self.b2, self.b3]})

    def test_typed_permutations(self):
        self.assertEqual(typed_permutations(self.problem.language.sorts, sort_constants(self.problem.language)),
                         [(self.b1,), (self.b2,), (self.b3,)])

    def test_fill_in_action(self):
        ground_actions = get_ground_action(self.problem.actions['pickup'], sort_constants(self.problem.language))
        for a in ground_actions:
            self.assertFalse(has_params(a))  # check whether the parameters of the action are all filled in


if __name__ == '__main__':
    unittest.main()
