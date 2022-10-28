import unittest

from dlplan import PolicyReader

from main import pddl_to_dlplan_states
from src.sketch_to_ltl import *


class ToLTLTest(unittest.TestCase):

    def setUp(self) -> None:
        vocabulary_info = dlplan.VocabularyInfo()
        vocabulary_info.add_predicate("unary", 1)
        factory = dlplan.SyntacticElementFactory(vocabulary_info)
        h = factory.parse_boolean("b_empty(c_primitive(unary,0))")
        n = factory.parse_numerical("n_count(c_primitive(unary,0))")

        builder = dlplan.PolicyBuilder()
        b_h = builder.add_boolean_feature(h)
        b_n = builder.add_numerical_feature(n)

        self.h_neg_condition_0 = builder.add_neg_condition(b_h)
        self.h_pos_condition_0 = builder.add_pos_condition(b_h)
        self.h_pos_effect_0 = builder.add_pos_effect(b_h)
        self.h_pos_effect_1 = builder.add_pos_effect(b_h)
        self.h_neg_effect_0 = builder.add_neg_effect(b_h)
        self.n_gt_condition_0 = builder.add_gt_condition(b_n)
        self.n_dec_effect_0 = builder.add_dec_effect(b_n)

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
        c_h_neg = self.p1.get_rules()[0].get_conditions()[0]
        c_n_gt = self.p1.get_rules()[0].get_conditions()[1]
        c_h_pos = self.p1.get_rules()[1].get_conditions()[0]

        self.assertEqual(num_ltl_p1.conditions,
                         [Top() & Var(c_h_neg) & Var(c_n_gt), (Top() & Var(c_h_pos)) & Var(c_n_gt)])


if __name__ == '__main__':
    unittest.main()
