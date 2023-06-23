import unittest
import dlplan
import dlplan.policy as dlpolicy
import ltl
import src.transition_system as ts
from src.logics.conditions_effects import *
from src.logics.feature_vars import NumericalVar, BooleanVar
from src.logics.rules import Sketch, SketchRule, LTLSketch, LTLRule


def compare_ltl_sketches(s1: LTLSketch, s2: LTLSketch):
    # Only works if rules are in the same order!!!
    for r1, r2 in zip(s1.rules, s2.rules):
        if not(r1.conditions == r2.conditions and r1.effects == r2.effects):
            return False

    return True


class SketchFromPolicyTest(unittest.TestCase):
    def get_factory(self, domain_file: str, instance_file: str):
        dproblem = ts.load_domain(domain_file)
        iproblem = ts.load_instance(domain_file, instance_file)
        i = ts.dlinstance_from_tarski(dproblem, iproblem)

        return dlplan.core.SyntacticElementFactory(i.get_vocabulary_info())

    def test_blocks_clear_(self):
        factory = self.get_factory("domains/blocks_4_clear/domain.pddl",
                                   "domains/blocks_4_clear/p-3-0.pddl")

        """
        {} -> {h, n=}
        {n>0} -> {¬h, n↓}
        """
        builder_0 = dlpolicy.PolicyBuilder()
        sketch_0: dlpolicy.Policy = dlpolicy.PolicyReader().read('(:policy\n'
                                                             '(:boolean_features "b_nullary(arm-empty)")\n'
                                                             '(:numerical_features "n_count(c_primitive(on,0))")\n'
                                                             '(:rule (:conditions ) (:effects (:e_b_pos 0) (:e_n_bot 0)))\n'
                                                             '(:rule (:conditions (:c_n_gt 0)) (:effects (:e_b_neg 0) (:e_n_dec 0)))\n'
                                                             ')', builder_0, factory)

        h = sketch_0.get_booleans().pop().compute_repr()
        n = sketch_0.get_numericals().pop().compute_repr()
        sketch = Sketch.from_policy(sketch_0)

        wanted_sketch: Sketch = Sketch([
            SketchRule([CGreater(n)], [ENegative(h), EDecr(n)]),
            SketchRule([], [EPositive(h), ENEqual(n)])
        ])

        self.assertEqual(sketch.rules, wanted_sketch.rules)

        wanted_ltl_0 = LTLSketch([
            LTLRule(NumericalVar(data=n, value=1), BooleanVar(data=h, value=False) & NumericalVar(data=n, value=0)),
             LTLRule(NumericalVar(data=n, value=2), (NumericalVar(data=n, value=0) | NumericalVar(data=n, value=1)) & BooleanVar(data=h, value=False)),
             LTLRule(NumericalVar(data=n, value=0), BooleanVar(data=h, value=True) & NumericalVar(data=n, value=0)),
             LTLRule(NumericalVar(data=n, value=1), BooleanVar(data=h, value=True) & NumericalVar(data=n, value=1)),
             LTLRule(NumericalVar(data=n, value=2), BooleanVar(data=h, value=True) & NumericalVar(data=n, value=2))])

        compare_ltl_sketches(wanted_ltl_0, sketch.to_ltl({n: (0, 2)}))

    def test_blocks_on(self):
        factory = self.get_factory("domains/blocks_4_on/domain.pddl", "domains/blocks_4_on/p-3-0.pddl")

        """
        {¬b1} -> {n0=, b0=}
        {} -> {b0}
        {} -> {n0↓}
        """
        builder_0 = dlpolicy.PolicyBuilder()
        sketch_0: dlpolicy.Policy = dlpolicy.PolicyReader().read('(:policy\n'
                                                             '(:boolean_features "b_nullary(arm-empty)" "b_empty(c_and(c_not(c_equal(r_primitive(on,0,1),r_primitive(on_g,0,1))),c_primitive(clear,0)))")\n'
                                                             '(:numerical_features "n_count(c_primitive(on,0))")\n'
                                                             '(:rule (:conditions ) (:effects (:e_b_pos 1)))\n'
                                                             '(:rule (:conditions ) (:effects (:e_n_dec 0)))\n'
                                                             '(:rule (:conditions (:c_b_neg 0)) (:effects (:e_b_bot 1) (:e_n_bot 0)))\n'
                                                             ')', builder_0, factory)

        booleans = sketch_0.get_booleans()
        b0 = booleans.pop().compute_repr()
        b1 = booleans.pop().compute_repr()
        n = sketch_0.get_numericals().pop().compute_repr()
        sketch = Sketch.from_policy(sketch_0)

        wanted_sketch = Sketch([
            SketchRule([CNegative(b1)], [ENEqual(n), EBEqual(b0)]),
            SketchRule([], [EPositive(b0)]),
            SketchRule([], [EDecr(n)])
        ])

        self.assertEqual(wanted_sketch.rules, sketch.rules)

    def test_gripper(self):
        factory = self.get_factory("domains/gripper/domain.pddl", "domains/gripper/p-3-0.pddl")
        v: dlplan.core.VocabularyInfo = factory.get_vocabulary_info()
        v.get_predicates()

        builder_1 = dlpolicy.PolicyBuilder()
        policy_1: dlpolicy.Policy = dlpolicy.PolicyReader().read('(:policy\n'
                                                             '(:boolean_features)\n'
                                                             '(:numerical_features "n_count(c_primitive(at,0))" "n_count(c_some(r_primitive(at,0,1),c_one_of(rooma)))")\n'
                                                             '(:rule (:conditions) (:effects (:e_n_dec 1)))\n'
                                                             '(:rule (:conditions) (:effects (:e_n_bot 1) (:e_n_inc 0)))\n'
                                                             ')', builder_1, factory)

        numericals = policy_1.get_numericals()
        g = numericals.pop().compute_repr()
        ga = numericals.pop().compute_repr()
        sketch_1 = Sketch.from_policy(policy_1)

        wanted_sketch_1 = Sketch([
            SketchRule([], [EDecr(ga)]),
            SketchRule([], [EIncr(g), ENEqual(ga)])
        ])

        self.assertEqual(wanted_sketch_1.rules, sketch_1.rules)



if __name__ == '__main__':
    unittest.main()
