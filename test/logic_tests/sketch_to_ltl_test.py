import unittest

import ltl

from src.logics.sketch_to_ltl import *
from src.dlplan_utils import *
from test.utils import ass_same_elements


# FIXME lists in assertion differ sometimes because the order of conditions doesn't matter

class ToLTLTest(unittest.TestCase):

    def setUp(self) -> None:
        vocabulary_info = dlplan.VocabularyInfo()
        vocabulary_info.add_predicate("unary", 1)
        vocabulary_info.add_predicate("a", 1)
        vocabulary_info.add_predicate("b", 1)
        vocabulary_info.add_predicate("c", 1)
        factory = dlplan.SyntacticElementFactory(vocabulary_info)
        self.a = factory.parse_boolean("b_empty(c_primitive(a,0))")
        self.b = factory.parse_boolean("b_empty(c_primitive(b,0))")
        self.c = factory.parse_boolean("b_empty(c_primitive(c,0))")
        self.d = factory.parse_boolean("b_empty(c_primitive(unary,0))")
        self.e = factory.parse_boolean("b_empty(c_primitive(unary,0))")
        self.h = factory.parse_boolean("b_empty(c_primitive(unary,0))")

        self.n = factory.parse_numerical("n_count(c_primitive(unary,0))")
        self.m = factory.parse_numerical("n_count(c_not(c_primitive(unary,0)))")
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

    def test_arrow_ltl(self):
        num_ltl_p1 = policy_to_arrowsketch(self.p1)

        # hack because equality between conditions and effects is not well-defined;
        # the condition in a rule is not equal to the condition that was put into the rule
        # i.e. in the following c_h_neg != self.h_neg_condition_0 which is counterintuitive
        h = self.p1.get_rules()[0].get_conditions()[0].get_base_feature()
        n = self.p1.get_rules()[0].get_conditions()[1].get_base_feature()

        rules = [ArrowLTLRule(Var(CNegative(h)) & Var(CGreater(n)), Var(EPositive(h)) & Var(EDecr(n))),
                 ArrowLTLRule((Var(CPositive(h))) & Var(CGreater(n)), Var(ENegative(h)))]
        self.assertEqual(rules, num_ltl_p1.rules)

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
        r1 = RuleListRepr([CPositive(self.h)], [[EDecr(self.n)]])
        r2 = RuleListRepr([CPositive(self.h)], [[ENegative(self.h)]])
        self.assertEqual([RuleListRepr([CPositive(self.h)], [[EDecr(self.n)], [ENegative(self.h)]])],
                         merge_rules(r1, r2))

        # conditions of one rule are a subset of the conditions of the other rule
        r3 = RuleListRepr([CPositive(self.h), CZero(self.n)], [[ENegative(self.h)]])
        r4 = RuleListRepr([CPositive(self.h)], [[EIncr(self.n)]])
        merged34 = [RuleListRepr({CPositive(self.h), CGreater(self.n)}, [[EIncr(self.n)]]),
                    RuleListRepr({CPositive(self.h), CZero(self.n)}, [[ENegative(self.h)], [EIncr(self.n)]])]
        self.assertEqual(merged34, merge_rules(r3, r4))

        # the non overlapping conditions are independent
        r5 = RuleListRepr([CPositive(self.a), CPositive(self.b)], [[CNegative(self.a)]])
        r6 = RuleListRepr([CPositive(self.a), CPositive(self.c)], [[CNegative(self.b)]])
        merged56 = [RuleListRepr({CPositive(self.a), CPositive(self.b), CNegative(self.c)}, [[CNegative(self.a)]]),
                    RuleListRepr({CPositive(self.a), CNegative(self.b), CPositive(self.c)}, [[CNegative(self.b)]]),
                    RuleListRepr({CPositive(self.a), CPositive(self.b), CPositive(self.c)}, [[CNegative(self.a)], [CNegative(self.b)]])]
        self.assertEqual(merged56, merge_rules(r5, r6))

        # conditions have multiple non-overlapping elements
        r11 = RuleListRepr([CPositive(self.h), CPositive(self.a)], [[CNegative(self.a)]])
        r12 = RuleListRepr([CPositive(self.h), CPositive(self.b), CPositive(self.c)], [[CNegative(self.b)]])
        merged1112 = [
            RuleListRepr({CPositive(self.h), CPositive(self.a), CNegative(self.b)}, [[CNegative(self.a)]]),
            RuleListRepr({CPositive(self.h), CPositive(self.a), CNegative(self.c)}, [[CNegative(self.a)]]),
            RuleListRepr({CPositive(self.h), CNegative(self.a), CPositive(self.b), CPositive(self.c)}, [[CNegative(self.b)]]),
            RuleListRepr({CPositive(self.h), CPositive(self.a), CPositive(self.b), CPositive(self.c)}, [[CNegative(self.a)], [CNegative(self.b)]])
        ]
        self.assertTrue(ass_same_elements(merged1112, merge_rules(r11, r12)))

        # all conditions are independent
        r7 = RuleListRepr({CPositive(self.h)}, [[ENegative(self.h)]])
        r8 = RuleListRepr({CGreater(self.n)}, [[EIncr(self.n)]])
        merged78 = [
            RuleListRepr({CPositive(self.h), CZero(self.n)}, [[ENegative(self.h)]]),
            RuleListRepr({CNegative(self.h), CGreater(self.n)}, [[EIncr(self.n)]]),
            RuleListRepr({CPositive(self.h), CGreater(self.n)}, [[ENegative(self.h)], [EIncr(self.n)]])
        ]

        self.assertEqual(merged78, merge_rules(r7, r8))

        # the rules shouldn't be merged
        r9 = RuleListRepr({CPositive(self.h), CZero(self.n)}, [[ENegative(self.a)]])
        r10 = RuleListRepr({CPositive(self.h), CGreater(self.n)}, [[ENegative(self.b)]])

        self.assertEqual([], merge_rules(r9, r10))

    def test_merge_all_rules(self):
        r1 = RuleListRepr({CPositive(self.a)}, [[ENegative(self.a)]])
        r2 = RuleListRepr({CPositive(self.b)}, [[ENegative(self.b)]])
        r3 = RuleListRepr({CPositive(self.c)}, [[ENegative(self.c)]])

        m123 = [RuleListRepr({CPositive(self.a), CPositive(self.b), CPositive(self.c)}, [[ENegative(self.a)], [ENegative(self.b)], [ENegative(self.c)]]),
                RuleListRepr({CPositive(self.a), CPositive(self.b), CNegative(self.c)}, [[ENegative(self.a)], [ENegative(self.b)]]),
                RuleListRepr({CPositive(self.a), CNegative(self.b), CPositive(self.c)}, [[ENegative(self.a)], [ENegative(self.c)]]),
                RuleListRepr({CPositive(self.a), CNegative(self.b), CNegative(self.c)}, [[ENegative(self.a)]]),
                RuleListRepr({CNegative(self.a), CPositive(self.b), CPositive(self.c)}, [[ENegative(self.b)], [ENegative(self.c)]]),
                RuleListRepr({CNegative(self.a), CPositive(self.b), CNegative(self.c)}, [[ENegative(self.b)]]),
                RuleListRepr({CNegative(self.a), CNegative(self.b), CPositive(self.c)}, [[ENegative(self.c)]]),
        ]

        self.assertEqual(m123, merge_all_rules([r1, r2, r3]))

        # same conditions
        r1a = RuleListRepr([CPositive(self.h)], [[EDecr(self.n)]])
        r2a = RuleListRepr([CPositive(self.h)], [[ENegative(self.h)]])
        self.assertEqual([RuleListRepr({CPositive(self.h)}, [[EDecr(self.n)], [ENegative(self.h)]])],
                         merge_all_rules([r1a, r2a]))

        # conditions of one rule are a subset of the conditions of the other rule
        r3a = RuleListRepr([CPositive(self.h), CZero(self.n)], [[ENegative(self.h)]])
        r4a = RuleListRepr([CPositive(self.h)], [[EIncr(self.n)]])
        merged34 = [
            RuleListRepr({CPositive(self.h), CZero(self.n)}, [[ENegative(self.h)], [EIncr(self.n)]]),
            RuleListRepr({CPositive(self.h), CGreater(self.n)}, [[EIncr(self.n)]]),
        ]
        self.assertEqual(merged34, merge_all_rules([r3a, r4a]))

        # the non overlapping conditions are independent
        r5 = RuleListRepr([CPositive(self.a), CPositive(self.b)], [[CNegative(self.a)]])
        r6 = RuleListRepr([CPositive(self.a), CPositive(self.c)], [[CNegative(self.b)]])
        merged56 = [RuleListRepr({CPositive(self.a), CPositive(self.b), CPositive(self.c)}, [[CNegative(self.a)], [CNegative(self.b)]]),
                    RuleListRepr({CPositive(self.a), CPositive(self.b), CNegative(self.c)}, [[CNegative(self.a)]]),
                    RuleListRepr({CPositive(self.a), CNegative(self.b), CPositive(self.c)}, [[CNegative(self.b)]])
                    ]

        self.assertEqual(merged56, merge_all_rules([r5, r6]))

        # conditions have multiple non-overlapping elements
        r11 = RuleListRepr([CPositive(self.h), CPositive(self.a)], [[CNegative(self.a)]])
        r12 = RuleListRepr([CPositive(self.h), CPositive(self.b), CPositive(self.c)], [[CNegative(self.b)]])
        merged1112 = [
            RuleListRepr({CPositive(self.h), CPositive(self.a), CPositive(self.b), CPositive(self.c)}, [[CNegative(self.a)], [CNegative(self.b)]]),
            RuleListRepr({CPositive(self.h), CPositive(self.a), CPositive(self.b), CNegative(self.c)}, [[CNegative(self.a)]]),
            RuleListRepr({CPositive(self.h), CPositive(self.a), CNegative(self.b), CPositive(self.c)}, [[CNegative(self.a)]]),
            RuleListRepr({CPositive(self.h), CPositive(self.a), CNegative(self.b), CNegative(self.c)}, [[CNegative(self.a)]]),
            RuleListRepr({CPositive(self.h), CNegative(self.a), CPositive(self.b), CPositive(self.c)}, [[CNegative(self.b)]]),

        ]

        self.assertTrue(ass_same_elements(merged1112, merge_all_rules([r11, r12])))

        # all conditions are independent
        r7 = RuleListRepr({CPositive(self.h)}, [[ENegative(self.h)]])
        r8 = RuleListRepr({CGreater(self.n)}, [[EIncr(self.n)]])
        merged78 = [
            RuleListRepr({CPositive(self.h), CZero(self.n)}, [[ENegative(self.h)]]),
            RuleListRepr({CPositive(self.h), CGreater(self.n)}, [[ENegative(self.h)], [EIncr(self.n)]]),
            RuleListRepr({CNegative(self.h), CGreater(self.n)}, [[EIncr(self.n)]])
        ]

        self.assertEqual(merged78, merge_all_rules([r7, r8]))

        # the rules shouldn't be merged
        r9 = RuleListRepr({CPositive(self.h), CZero(self.n)}, [[ENegative(self.a)]])
        r10 = RuleListRepr({CPositive(self.h), CGreater(self.n)}, [[ENegative(self.b)]])

        self.assertEqual([r9, r10], merge_all_rules([r9, r10]))

    def test_bound_fill_in(self):
        bound_dict = {self.n: 2, self.m: 2, self.o: 3}

        rules = [ArrowLTLRule(Var(CGreater(self.n)), Var(EDecr(self.n))), ArrowLTLRule(Var(CPositive(self.a)), Var(ENegative(self.a)))]

        rs = fill_in_rules(rules, bound_dict)

        wanted_rs = [LTLRule(NumericalVar(self.n, 1), NumericalVar(self.n, 0)),
                     LTLRule(NumericalVar(self.n, 2), NumericalVar(self.n, 0) | NumericalVar(self.n, 1)),
                     LTLRule(BooleanVar(self.a, True), BooleanVar(self.a, False))
                     ]
        self.assertEqual(rs, wanted_rs)

        rules_2 = [ArrowLTLRule(Var(CZero(self.n)), Var(EDecr(self.m)))]
        rs_2 = fill_in_rules(rules_2, bound_dict)

        wanted_rs_2 = [
            LTLRule(NumericalVar(self.m, 0) & NumericalVar(self.n, 0), NumericalVar(self.m, 0)),
            LTLRule(NumericalVar(self.m, 1) & NumericalVar(self.n, 0), NumericalVar(self.m, 0)),
            LTLRule(NumericalVar(self.m, 2) & NumericalVar(self.n, 0), NumericalVar(self.m, 0) | NumericalVar(self.m, 1)),
        ]

        self.assertEqual(rs_2, wanted_rs_2)





if __name__ == '__main__':
    unittest.main()
