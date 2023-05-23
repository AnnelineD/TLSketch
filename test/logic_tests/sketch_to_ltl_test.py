import unittest

import ltl

from src.dlplan_utils import *
from src.logics.conditions_effects import *
from src.logics.feature_vars import NumericalVar, BooleanVar
from src.logics.rules import Sketch, SketchRule, LTLRule, LTLSketch
from test.utils import ass_same_elements


# FIXME lists in assertion differ sometimes because the order of conditions doesn't matter

def compare_ltl_sketches(s1: LTLSketch, s2: LTLSketch):
    # Only works if rules are in the same order!!!
    for r1, r2 in zip(s1.rules, s2.rules):
        if not(r1.conditions == r2.conditions and r1.effects == r2.effects):
            return False

    return True


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

    def test_bound_fill_in(self):
        bound_dict = {"n_n": (0, 2), "n_m": (0, 2), "n_o": (1, 3)}
        sketch = Sketch([SketchRule([CGreater('n_n')], [EDecr('n_n')]), SketchRule([CPositive('b_a')], [ENegative('b_a')])])

        ltl_sketch = sketch.to_ltl(bound_dict)

        wanted_ltl_sketch = LTLSketch([LTLRule(NumericalVar('n_n', 1), NumericalVar('n_n', 0)),
                                       LTLRule(NumericalVar('n_n', 2), NumericalVar('n_n', 0) | NumericalVar('n_n', 1)),
                                       LTLRule(BooleanVar('b_a', True), BooleanVar('b_a', False))
                                       ])

        for e, r in enumerate(ltl_sketch.rules):
            print(e, r.conditions.show(), r.effects.show())
        self.assertTrue(compare_ltl_sketches(ltl_sketch, wanted_ltl_sketch))

        sketch_2 = Sketch([SketchRule([CZero('n_n')], [EDecr('n_o')])])
        ltl_sketch_2 = sketch_2.to_ltl(bound_dict)

        wanted_ltl_sketch_2 = LTLSketch([
            LTLRule(NumericalVar('n_n', 0) & NumericalVar('n_o', 2), NumericalVar('n_o', 1)),
            LTLRule(NumericalVar('n_n', 0) & NumericalVar('n_o', 3), NumericalVar('n_o', 1) | NumericalVar('n_o', 2)),
        ])

        for e, r in enumerate(ltl_sketch_2.rules):
            print(e, r.conditions.show(), '\t',  r.effects.show())

        self.assertTrue(compare_ltl_sketches(ltl_sketch_2, wanted_ltl_sketch_2))






if __name__ == '__main__':
    unittest.main()
