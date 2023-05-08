import unittest

import ctl

from src.logics.feature_vars import FeatureVar
from src.logics.rules import LTLSketch, LTLRule
from src.sketch_verification.feature_instance import FeatureInstance
from src.sketch_verification.verify import check_file, verification
from src.logics.laws import AbstractLaw, Law
import ltl

from src.transition_system.graph import DirectedGraph


class SketchVerification(unittest.TestCase):

    def setUp(self) -> None:
        self.law_ltl_true = Law(ltl.Globally(ltl.Top()), True)
        self.law_ltl_false = Law(ltl.Globally(ltl.Bottom()), False)

        self.law_ctl_true = Law(ctl.AG(ctl.Top()), True)
        self.law_ctl_false = Law(ctl.EF(ctl.Bottom()), False)

        graph1 = DirectedGraph([[[1], ["1"]], [[2], ["2"]], [[2], [""]]])
        feature_vals1 = {"b": [False, True, False]}
        self.instance1 = FeatureInstance(graph1, 0, [2], feature_vals1)

        self.ltl_sketch1 = LTLSketch([LTLRule(FeatureVar("b", True), ltl.Not(FeatureVar("b", True))),
                                      LTLRule(ltl.Not(FeatureVar("b", True)), FeatureVar("b", True))])

        self.law_c0_or_c1 = Law(ctl.AG(ctl.Or(ctl.Var("c0"), ctl.Var("c1"))), True)
        self.law_c0 = Law(ctl.AG(ctl.Var("c0")), False)

    def test_verify_from_file(self):
        self.assertTrue(check_file("blocks_clear_0.smv", [self.law_ltl_true, self.law_ltl_false, self.law_ctl_true, self.law_ctl_false]))

    def test_verification(self):
        self.assertTrue(verification(self.ltl_sketch1, self.instance1, [self.law_c0_or_c1, self.law_c0]))


if __name__ == '__main__':
    unittest.main()
