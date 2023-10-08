import unittest
from functools import reduce
import ltl
from src.logics.laws import *


class ExpandLawTest(unittest.TestCase):
    def test_expand(self):
        def mock_law(n: int) -> LTLFormula:
            return reduce(ltl.And, [ltl.Var(f"v{i}") for i in range(n)])
        abslaw = AbstractLaw(mock_law, True)

        self.assertEqual(ltl.And(ltl.Var('v0'), ltl.Var('v1')),
                         abslaw.expand(2).formula)

        self.assertEqual(ltl.And(ltl.And(ltl.And(ltl.And(ltl.Var('v0'), ltl.Var('v1')), ltl.Var('v2')), ltl.Var('v3')), ltl.Var('v4')),
                         abslaw.expand(5).formula)

        # abslaw.expand(0).formula TODO catch TypeError: reduce() of empty iterable with no initial value error


if __name__ == '__main__':
    unittest.main()
