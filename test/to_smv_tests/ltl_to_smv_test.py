import unittest
from ltl import *

from src.logics.feature_vars import BooleanVar, NumericalVar
from src.to_smv.conversion import ltl_to_smv


class LTLToSMV(unittest.TestCase):

    def test_with_boolean(self):
        b = BooleanVar("b_1", True)

        self.assertEqual("b_1=TRUE", ltl_to_smv(b))
        self.assertEqual("X((b_1=TRUE & TRUE))", ltl_to_smv(Next(b & Top())))
        self.assertEqual("G((F(b_1=TRUE) | F(!b_1=TRUE)))", ltl_to_smv(Globally(Finally(b) | Finally(Not(b)))))

    def test_with_numerical(self):
        n = NumericalVar("n_0", 1)

        self.assertEqual("n_0=1", ltl_to_smv(n))
        self.assertEqual("X((n_0=1 & TRUE))", ltl_to_smv(Next(n & Top())))
        self.assertEqual("G((F(n_0=1) | F(!n_0=1)))", ltl_to_smv(Globally(Finally(n) | Finally(Not(n)))))

    def test_with_bad_var(self):
        # TODO
        pass

    def test_with_bound(self):
        n = NumericalVar("n_0", 1)

        self.assertEqual("F[1, 3](n_0=1)", ltl_to_smv(Finally(n, (1, 3))))
        self.assertEqual("G((F[1, 3](n_0=1) | O[5, 7](!n_0=1)))", ltl_to_smv(Globally(Finally(n, (1, 3)) | Once(Not(n), (5, 7)))))


if __name__ == '__main__':
    unittest.main()
