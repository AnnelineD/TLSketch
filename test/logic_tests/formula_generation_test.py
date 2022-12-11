import unittest

from ltl import *

from src.logics.formula_generation import FormulaGenerator


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(
            Globally(Var('c0') | Var('c1') | Var('c2') | Var('goal') | ~(Finally(Var('goal')))),
            FormulaGenerator(3).one_condition())


if __name__ == '__main__':
    unittest.main()
