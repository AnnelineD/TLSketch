import unittest
from functools import reduce
from typing import Union

import ctl
import ltl

from src.logics.laws import AbstractLaw
from src.logics.rules import Sketch
from src.sketch_verification.feature_instance import FeatureInstance
from src.sketch_verification.laws import simple_law, exists_simple_law, impl_law, exists_impl_law
from src.sketch_verification.verify import verify_sketch
from examples import *
import src.file_manager as fm


class VerifyExamples(unittest.TestCase):

    def setUp(self) -> None:
        ltl_conditions = lambda n: [ltl.Var(f'c{i}') for i in range(n)]
        ltl_effects = lambda n: [ltl.Var(f'e{i}') for i in range(n)]
        self.rules = lambda n: list(zip(ltl_conditions(n), ltl_effects(n)))
        ctl_conditions = lambda n: [ctl.Var(f'c{i}') for i in range(n)]
        ctl_effects = lambda n: [ctl.Var(f'e{i}') for i in range(n)]
        self.ctl_rules = lambda n: list(zip(ctl_conditions(n), ctl_effects(n)))
        self.ltl_goal = ltl.Var('goal')
        self.ctl_goal = ctl.Var('goal')

        def follow_rules(n) -> ltl.LTLFormula:
            return ltl.Globally(
                (reduce(ltl.Or, [e & (ltl.Once(c)) for c, e in self.rules(n)])
                 & reduce(ltl.Or, [c & (ltl.Finally(e)) for c, e in self.rules(n)]))
                | reduce(ltl.Or, [(ltl.Once(c)) & (ltl.Finally(e & (
                            reduce(ltl.Or, [cj & ltl.Finally(ej) for cj, ej in self.rules(n)]) | self.ltl_goal))) for c, e in self.rules(n)])
                | self.ltl_goal
            )

        # G((( ∨i (ei ∧ Oci)) ∧ ( ∨i (ci ∧ F ei))) ∨ (∨i(O(ci) ∧ F ei))) → F (goal)
        def rules_followed_then_goal(n) -> ltl.LTLFormula:
            return ltl.Then(
                follow_rules(n), ltl.Finally(self.ltl_goal)
            )

        def ctl_rule_cannot_lead_into_dead(n) -> ctl.CTLFormula:
            return reduce(ctl.And, [ctl.AG(ctl.Then(c, ctl.Not(ctl.EF(ctl.And(e, ctl.Not(ctl.EF(self.ctl_goal))))))) for c, e in self.ctl_rules(n)])

        def ctl_rule_can_be_followed(n) -> ctl.CTLFormula:
            return ctl.AG(ctl.Or(ctl.Or(reduce(ctl.Or, [ctl.And(c, ctl.EF(ctl.And(e, ctl.EF(self.ctl_goal)))) for c, e in self.ctl_rules(n)]), self.ctl_goal), ctl.Not(ctl.EF(self.ctl_goal))))

        self.law1 = AbstractLaw(ctl_rule_can_be_followed, True)
        self.law2 = AbstractLaw(ctl_rule_cannot_lead_into_dead, True)
        self.law3 = AbstractLaw(rules_followed_then_goal, True)

    def verify_existing_sketch(self, domain, sketch_n):
        # print("yes")
        policy = domain.sketches()[sketch_n]
        sketch = Sketch.from_policy(policy)
        features = policy.get_boolean_features() + policy.get_numerical_features()
        feature_vals: dict[str, list[Union[bool, int]]] = {f.compute_repr(): [f.evaluate(s) for s in domain.dl_states] for f in features}
        # print(feature_vals)
        instance = FeatureInstance(domain.transition_system.graph, domain.transition_system.init, domain.transition_system.goals, feature_vals)

        # print(impl_law.expand(2).formula.show())
        self.assertTrue(verify_sketch(sketch, instance, [impl_law, exists_impl_law]))

    def test_verify_Gripper(self):
        # self.verify_existing_sketch(Gripper(), 2)
        self.verify_existing_sketch(Gripper(), 1)
        # self.verify_existing_sketch(Gripper(), 0)

    def test_verify_Blocks_on(self):
        self.verify_existing_sketch(BlocksOn(), 2)
        self.verify_existing_sketch(BlocksOn(), 1)
        # self.verify_existing_sketch(BlocksOn(), 0)

    def test_verify_blocks_clear(self):
        self.verify_existing_sketch(BlocksClear(), 2)
        self.verify_existing_sketch(BlocksClear(), 1)
        # self.verify_existing_sketch(BlocksClear(), 0)

    def test_verify_miconic(self):
        self.verify_existing_sketch(Miconic(), 2)
        self.verify_existing_sketch(Miconic(), 1)

    def test_verify_childsnack(self):
        self.verify_existing_sketch(Childsnack(), 1)

    def test_verify_delivery(self):
        self.verify_existing_sketch(Delivery(), 2)


if __name__ == '__main__':
    unittest.main()
