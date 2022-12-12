import unittest
from unittest.mock import patch

import dlplan
from ltl import *

from src.logics.feature_vars import BooleanVar, NumericalVar
from src.to_smv.conversion import ltl_to_smv

dlplanb = dlplan.Boolean
dlplann = dlplan.Numerical


class MyTestCase(unittest.TestCase):

    @patch("dlplan.Boolean", autospec=dlplan.Boolean)
    def test_with_boolean(self, mock_b_constr):
        mock_b_constr.__class__ = dlplanb
        mock_b = mock_b_constr.return_value
        dlplan.Boolean = dlplanb
        b = BooleanVar(mock_b, True)
        mock_b.get_index.return_value = 0

        self.assertEqual("b0=TRUE", ltl_to_smv(b))
        self.assertEqual("X((b0=TRUE & TRUE))", ltl_to_smv(Next(b & Top())))
        self.assertEqual("G((F(b0=TRUE) | F(!b0=TRUE)))", ltl_to_smv(Globally(Finally(b) | Finally(Not(b)))))

    @patch("dlplan.Numerical", spec=dlplan.Numerical)
    def test_with_numerical(self, mock_n_constr):
        mock_n_constr.__class__ = dlplanb
        mock_n = mock_n_constr.return_value
        dlplan.Numerical = dlplann
        n = NumericalVar(mock_n, 1)
        mock_n.get_index.return_value = 0

        self.assertEqual("n0=1", ltl_to_smv(n))
        self.assertEqual("X((n0=1 & TRUE))", ltl_to_smv(Next(n & Top())))
        self.assertEqual("G((F(n0=1) | F(!n0=1)))", ltl_to_smv(Globally(Finally(n) | Finally(Not(n)))))

    def test_with_bad_var(self):
        self.assertIsNone(ltl_to_smv(Var(5)))


if __name__ == '__main__':
    unittest.main()
