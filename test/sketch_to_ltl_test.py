import unittest

from dlplan import PolicyReader

from main import pddl_to_dlplan_states
from src.sketch_to_ltl import *
from src.dlplan_utils import *


class ToLTLTest(unittest.TestCase):

    def setUp(self) -> None:
        vocabulary_info = dlplan.VocabularyInfo()
        vocabulary_info.add_predicate("unary", 1)
        factory = dlplan.SyntacticElementFactory(vocabulary_info)
        self.a = factory.parse_boolean("b_empty(c_primitive(unary,0))")
        self.b = factory.parse_boolean("b_empty(c_primitive(unary,0))")
        self.c = factory.parse_boolean("b_empty(c_primitive(unary,0))")
        self.h = factory.parse_boolean("b_empty(c_primitive(unary,0))")

        self.n = factory.parse_numerical("n_count(c_primitive(unary,0))")
        self.m = factory.parse_numerical("n_count(c_primitive(unary,0))")
        self.o = factory.parse_numerical("n_count(c_primitive(unary,0))")


        builder = dlplan.PolicyBuilder()
        b_h = builder.add_boolean_feature(self.h)
        b_n = builder.add_numerical_feature(self.n)

        self.h_neg_condition_0 = builder.add_neg_condition(b_h)     # con: ¬h
        self.h_pos_condition_0 = builder.add_pos_condition(b_h)     # con: h
        self.h_pos_effect_0 = builder.add_pos_effect(b_h)           # eff: h
        self.h_neg_effect_0 = builder.add_neg_effect(b_h)           # eff: ¬h
        self.h_bot_effect_0 = builder.add_bot_effect(b_h)           # eff: h?

        self.n_gt_condition_0 = builder.add_gt_condition(b_n)       # con: n>0
        self.n_eq_condition_0 = builder.add_eq_condition(b_n)       # con: n=0
        self.n_dec_effect_0 = builder.add_dec_effect(b_n)           # eff: n↓
        self.n_inc_effect_0 = builder.add_inc_effect(b_n)           # eff: n↑
        self.n_bot_effect_0 = builder.add_bot_effect(b_n)           # eff: n?

        # {!H, n>0} -> {H, n↓}
        builder.add_rule(
            [self.h_neg_condition_0, self.n_gt_condition_0],
            [self.h_pos_effect_0, self.n_dec_effect_0]
        )
        # {H, n > 0} → {¬H}
        builder.add_rule(
            [self.h_pos_condition_0, self.n_gt_condition_0],
            [self.h_neg_effect_0])

        self.p1 = builder.get_result()

    def test_num_ltl(self):
        num_ltl_p1 = to_num_ltl(self.p1)

        # hack because equality between conditions and effects is not well defined;
        # the condition in a rule is not equal to the condition that was put into the rule
        # i.e. in the following c_h_neg != self.h_neg_condition_0 which is counter intuitive
        h = self.p1.get_rules()[0].get_conditions()[0].get_base_feature()
        n = self.p1.get_rules()[0].get_conditions()[1].get_base_feature()

        self.assertEqual([Top() & Var(CNegative(h)) & Var(CGreater(n)),
                          (Top() & Var(CPositive(h))) & Var(CGreater(n))],
                         num_ltl_p1.conditions)

    def test_show(self):  # TODO maybe move this test to a separate file?
        self.assertEqual(show_condition(self.h_neg_condition_0, "H"), "¬H")
        self.assertEqual(show_condition(self.h_pos_condition_0, "H"), "H")
        self.assertEqual(show_effect(self.h_pos_effect_0, "H"), "H")
        self.assertEqual(show_effect(self.h_neg_effect_0, "H"), "¬H")
        self.assertEqual(show_effect(self.h_bot_effect_0, "H"), "H?")

        self.assertEqual(show_condition(self.n_gt_condition_0, "n"), "n>0")
        self.assertEqual(show_condition(self.n_eq_condition_0, "n"), "n=0")
        self.assertEqual(show_effect(self.n_dec_effect_0, "n"), "n↓")
        self.assertEqual(show_effect(self.n_inc_effect_0, "n"), "n↑")
        self.assertEqual(show_effect(self.n_bot_effect_0, "n"), "n?")

    def test_merge_rules(self):
        # same conditions
        r1 = RuleTupleRepr([CPositive(self.h)], [[EDecr(self.n)]])
        r2 = RuleTupleRepr([CPositive(self.h)], [[ENegative(self.h)]])
        self.assertEqual([RuleTupleRepr([CPositive(self.h)], [[EDecr(self.n)], [ENegative(self.h)]])],
                         merge_rules(r1, r2))

        # conditions of one rule are a subset of the conditions of the other rule
        r3 = RuleTupleRepr([CPositive(self.h), CZero(self.n)], [[ENegative(self.h)]])
        r4 = RuleTupleRepr([CPositive(self.h)], [[EIncr(self.n)]])
        merged34 = [RuleTupleRepr({CPositive(self.h), CGreater(self.n)}, [[EIncr(self.n)]]),
                    RuleTupleRepr({CPositive(self.h), CZero(self.n)}, [[ENegative(self.h)], [EIncr(self.n)]])]
        self.assertEqual(merged34, merge_rules(r3, r4))

        # the non overlapping conditions are independent
        r5 = RuleTupleRepr([CPositive(self.a), CPositive(self.b)], [[CNegative(self.a)]])
        r6 = RuleTupleRepr([CPositive(self.a), CPositive(self.c)], [[CNegative(self.b)]])
        merged56 = [RuleTupleRepr({CPositive(self.a), CPositive(self.b), CNegative(self.c)}, [[CNegative(self.a)]]),
                    RuleTupleRepr({CPositive(self.a), CNegative(self.b), CPositive(self.c)}, [[CNegative(self.b)]]),
                    RuleTupleRepr({CPositive(self.a), CPositive(self.b), CPositive(self.c)}, [[CNegative(self.a)], [CNegative(self.b)]])]
        self.assertEqual(merged56, merge_rules(r5, r6))

        # all conditions are independent
        r7 = RuleTupleRepr({CPositive(self.h)}, [[ENegative(self.h)]])
        r8 = RuleTupleRepr({CGreater(self.n)}, [[EIncr(self.n)]])
        merged78 = [
            RuleTupleRepr({CPositive(self.h), CZero(self.n)}, [[ENegative(self.h)]]),
            RuleTupleRepr({CNegative(self.h), CGreater(self.n)}, [[EIncr(self.n)]]),
            RuleTupleRepr({CPositive(self.h), CGreater(self.n)}, [[ENegative(self.h)], [EIncr(self.n)]])
        ]

        self.assertEqual(merged78, merge_rules(r7, r8))

        # the rules shouldn't be merged
        r9 = RuleTupleRepr({CPositive(self.h), CZero(self.n)}, [[ENegative(self.a)]])
        r10 = RuleTupleRepr({CPositive(self.h), CGreater(self.n)}, [[ENegative(self.b)]])

        self.assertEqual([], merge_rules(r9, r10))




if __name__ == '__main__':
    unittest.main()
