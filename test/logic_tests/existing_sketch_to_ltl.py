import unittest
import dlplan

import src.dlplan_utils
from src.logics.sketch_to_ltl import *
from src.transition_system.conversions import dlinstance_from_tarski
from src.transition_system.tarski import *


class MyTestCase(unittest.TestCase):
    def get_factory(self, domain_file: str, instance_file: str):
        dproblem, iproblem = load_domain_instance(domain_file, instance_file)
        i = dlinstance_from_tarski(dproblem, iproblem)

        return dlplan.SyntacticElementFactory(i.get_vocabulary_info())

    def test_blocks_clear(self):
        factory = self.get_factory("../../blocks_4_clear/domain.pddl", "../../blocks_4_clear/p-3-0.pddl")

        """
        {} -> {h, n=}
        {n>0} -> {¬h, n↓}
        """
        sketch_0: dlplan.Policy = dlplan.PolicyReader().read('(:policy\n'
                                                             '(:boolean_features "b_nullary(arm-empty)")\n'
                                                             '(:numerical_features "n_count(c_primitive(on,0))")\n'
                                                             '(:rule (:conditions ) (:effects (:e_b_pos 0) (:e_n_bot 0)))\n'
                                                             '(:rule (:conditions (:c_n_gt 0)) (:effects (:e_b_neg 0) (:e_n_dec 0)))\n'
                                                             ')', factory)

        h = sketch_0.get_boolean_features()[0]
        n = sketch_0.get_numerical_features()[0]
        arrow_sketch_0 = policy_to_arrowsketch(sketch_0)

        wanted_rules_0: list[ArrowLTLRule] = [
                ArrowLTLRule(Var(CZero(n)), Var(EPositive(h)) & Var(ENAny(n))),
                ArrowLTLRule(Var(CGreater(n)), (Var(ENegative(h)) & Var(EDecr(n))) | (Var(EPositive(h)) & Var(ENAny(n))))
            ]

        self.assertEqual(wanted_rules_0, arrow_sketch_0.rules)

        wanted_ltl_0 = [
            LTLRule(NumericalVar(n, 0), BooleanVar(h, True) & NumericalVar(n, 0)),
            LTLRule(NumericalVar(n, 1), ((BooleanVar(h, False) & NumericalVar(n, 0)) | (BooleanVar(h, True) & NumericalVar(n, 1)))),
            LTLRule(NumericalVar(n, 2), ((BooleanVar(h, False) & (NumericalVar(n, 0) | NumericalVar(n, 1))) | (BooleanVar(h, True) & NumericalVar(n, 2))))
        ]

        self.assertEqual(wanted_ltl_0, fill_in_rules(arrow_sketch_0.rules, {n: 2}))

    def test_blocks_on(self):
        factory = self.get_factory("../../blocks_4_on/domain.pddl", "../../blocks_4_on/p-3-0.pddl")

        """
        {¬b1} -> {n0=, b0=}
        {} -> {b0}
        {} -> {n0↓}
        """
        sketch_0: dlplan.Policy = dlplan.PolicyReader().read('(:policy\n'
                                                             '(:boolean_features "b_nullary(arm-empty)" "b_empty(c_and(c_not(c_equal(r_primitive(on,0,1),r_primitive(on_g,0,1))),c_primitive(clear,0)))")\n'
                                                             '(:numerical_features "n_count(c_primitive(on,0))")\n'
                                                             '(:rule (:conditions ) (:effects (:e_b_pos 1)))\n'
                                                             '(:rule (:conditions ) (:effects (:e_n_dec 0)))\n'
                                                             '(:rule (:conditions (:c_b_neg 0)) (:effects (:e_b_bot 1) (:e_n_bot 0)))\n'
                                                             ')', factory)

        b0 = sketch_0.get_boolean_features()[0]
        b1 = sketch_0.get_boolean_features()[1]
        n = sketch_0.get_numerical_features()[0]
        arrow_sketch_0 = policy_to_arrowsketch(sketch_0)

        wanted_rules_0: list[ArrowLTLRule] = [
            ArrowLTLRule(Var(CPositive(b1)), Var(EPositive(b0)) | Var(EDecr(n))),
            ArrowLTLRule(Var(CNegative(b1)), (((Var(ENAny(n)) & Var(EBAny(b0))) | Var(EPositive(b0))) | Var(EDecr(n))))
        ]

        self.assertEqual(wanted_rules_0, arrow_sketch_0.rules)

    def test_gripper(self):
        factory = self.get_factory("../../gripper/domain.pddl", "../../gripper/p-3-0.pddl")
        v: dlplan.VocabularyInfo = factory.get_vocabulary_info()
        v.get_predicates()

        sketch_1: dlplan.Policy = dlplan.PolicyReader().read('(:policy\n'
                                                             '(:boolean_features)\n'
                                                             '(:numerical_features "n_count(c_primitive(at,0))" "n_count(c_some(r_primitive(at,0,1),c_one_of(rooma)))")\n'
                                                             '(:rule (:conditions) (:effects (:e_n_dec 1)))\n'
                                                             '(:rule (:conditions) (:effects (:e_n_bot 1) (:e_n_inc 0)))\n'
                                                             ')', factory)

        g = sketch_1.get_numerical_features()[0]
        ga = sketch_1.get_numerical_features()[1]
        arrow_sketch_1 = policy_to_arrowsketch(sketch_1)
        wanted_rules_1 = [
            ArrowLTLRule(Top(), Var(EDecr(ga)) | (Var(EIncr(g)) & Var(ENAny(ga))))
        ]

        self.assertEqual(wanted_rules_1, arrow_sketch_1.rules)



if __name__ == '__main__':
    unittest.main()
