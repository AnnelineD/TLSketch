import unittest
import dlplan

from src.logics.conditions_effects import *
from src.logics.rules import Sketch, SketchRule, ExpandedSketch, ExpandedRule
from src.logics.feature_vars import NumericalVar, BooleanVar


class ExpandedRuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.r1 = ExpandedRule([NumericalVar('n', 5, '=')], [BooleanVar('b', False, '=')])
        self.r2 = ExpandedRule([NumericalVar('n', 5, '='), BooleanVar('b', True, '=')],
                               [NumericalVar('n', 4, '='), BooleanVar('b', False, '=')])

    def test_equality(self):
        self.assertEqual(self.r1, self.r1)
        test1 = ExpandedRule([NumericalVar('n', 5, '=')], [BooleanVar('b', False, '=')])
        # TODO write good equality function for rules and sketches
        # self.assertEqual(test1, self.r1)

    def test_show(self):
        self.assertEqual('conditions: "n=5"    effects: "!b"', self.r1.show())
        self.assertEqual('conditions: "n=5", "b"    effects: "n=4", "!b"', self.r2.show())

    def test_get_features(self):
        self.assertSetEqual({'n', 'b'}, self.r1.get_features())
        self.assertSetEqual({'n', 'b'}, self.r2.get_features())


class ExpandedSketchTest(unittest.TestCase):
    def setUp(self) -> None:
        r1 = ExpandedRule([NumericalVar('n', 5, '=')], [BooleanVar('b', False, '=')])
        r2 = ExpandedRule([NumericalVar('n', 5, '='), BooleanVar('b', True, '=')],
                          [NumericalVar('n', 4, '='), BooleanVar('b', False, '=')])

        self.s0 = ExpandedSketch([])
        self.s1 = ExpandedSketch([r1, r2])

    def test_n_rules(self):
        self.assertEqual(0, self.s0.n_rules())
        self.assertEqual(2, self.s1.n_rules())
        self.assertEqual(1, ExpandedSketch([ExpandedRule([], [])]).n_rules())

    def test_get_features(self):
        self.assertSetEqual(set(), self.s0.get_features())
        self.assertSetEqual({'n', 'b'}, self.s1.get_features())


class SketchRuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.r1 = SketchRule([CGreater('n')], [ENegative('b')])
        self.r2 = SketchRule([CGreater('n'), CPositive('b')],
                             [EDecr('n'), ENegative('b')])

    def test_equality(self):
        self.assertEqual(self.r1, self.r1)
        r1bis = SketchRule([CGreater('n')], [ENegative('b')])

        self.assertEqual(r1bis, self.r1)

        r2difforder = SketchRule([CPositive('b'), CGreater('n')],
                                 [EDecr('n'), ENegative('b')])

        # Sketchrules are only equal if the conditions and effects are in the same order.
        # TODO write a better equality function for sketchrules
        self.assertNotEqual(r2difforder, self.r2)

    def test_from_dlplan_rule(self):
        pass

    def test_from_tuple(self):
        self.assertEqual(self.r1, SketchRule.from_tuple(([CGreater('n')], [ENegative('b')])))
        self.assertEqual(self.r2, SketchRule.from_tuple(([CGreater('n'), CPositive('b')],
                                                         [EDecr('n'), ENegative('b')])))

    def test_deserialize(self):
        self.assertEqual(self.r1, SketchRule.deserialize((["CGreater('n')"], ["ENegative('b')"])))
        self.assertEqual(self.r2, SketchRule.deserialize((["CGreater('n')", "CPositive('b')"],
                                                          ["EDecr('n')", "ENegative('b')"])))

    def test_serialize(self):
        self.assertEqual((["CGreater(feature='n')"], ["ENegative(feature='b')"]), self.r1.serialize())
        self.assertEqual((["CGreater(feature='n')", "CPositive(feature='b')"],
                          ["EDecr(feature='n')", "ENegative(feature='b')"]), self.r2.serialize())

    def test_get_condition_features(self):
        self.assertSetEqual({'n'}, self.r1.get_condition_features())
        self.assertSetEqual({'n', 'b'}, self.r2.get_condition_features())

    def test_get_effect_features(self):
        self.assertSetEqual({'b'}, self.r1.get_effect_features())
        self.assertSetEqual({'n', 'b'}, self.r2.get_effect_features())

    def test_get_features(self):
        self.assertSetEqual({'n', 'b'}, self.r1.get_features())
        self.assertSetEqual({'n', 'b'}, self.r2.get_features())

    def test_simplify(self):
        self.assertEqual(SketchRule([CPositive("n")], [ENEqual("n")]),
                         SketchRule([CPositive("n"), CNAny("n")], [ENEqual("n"), EBAny("b")]).simplify())

    def test_expand(self):
        # TODO
        # tests for expanding sketches are in other files
        pass


class SketchTest(unittest.TestCase):
    def test_contains(self):
        r1 = SketchRule([CGreater("f1")], [EDecr("f1")])
        r2 = SketchRule([CGreater("f2")], [EDecr("f2")])
        r3 = SketchRule([CGreater("f3")], [EDecr("f3")])
        r4 = SketchRule([CGreater("f1"), CGreater("f2")], [EDecr("f1"), EDecr("f2")])
        r5 = SketchRule([CGreater("f3"), CGreater("f2")], [EDecr("f3"), EDecr("f2")])
        r6 = SketchRule([CGreater("f3"), CGreater("f4")], [EDecr("f3"), EDecr("f4")])

        ls1 = [Sketch([r1]), Sketch([r2])]
        ls2 = [Sketch([r1, r2]), Sketch([r3, r4]), Sketch([r1, r3])]
        ls3 = [Sketch([r3, r4, r5]), Sketch([r3, r5, r6]), Sketch([r2, r5, r6])]

        self.assertTrue(Sketch([r1, r2]).contains_sketch(Sketch([r1, r2])))
        self.assertTrue(Sketch([r5, r6]).contains_sketch(Sketch([r5, r6])))

        self.assertTrue(Sketch([r1, r2]).contains_sketch(Sketch([r1])))
        self.assertTrue(Sketch([r5, r6]).contains_sketch(Sketch([r5])))

        self.assertTrue(Sketch([r1, r2, r3]).contains_sketch(Sketch([r1, r2])))

        self.assertFalse(Sketch([r1, r2, r3]).contains_sketch(Sketch([r1, r4])))

        s_1 = Sketch.deserialize([([], ["EIncr(feature='n_count(c_equal(r_primitive(on,0,1),r_primitive(on_g,0,1)))')",
                                        "EPositive(feature='b_nullary(arm-empty)')"])])
        s_2 = Sketch.deserialize([([], ["EIncr(feature='n_count(c_equal(r_primitive(on,0,1),r_primitive(on_g,0,1)))')",
                                        "EPositive(feature='b_nullary(arm-empty)')"]),
                                  ([], ["EIncr(feature='n_count(c_equal(r_primitive(on,0,1),r_primitive(on_g,0,1)))')",
                                        "ENegative(feature='b_nullary(arm-empty)')"])])
        self.assertTrue(s_2.contains_sketch(s_1))

    def test_simplify(self):
        s1 = Sketch([SketchRule([CNAny("n"), CBAny("b")], [ENAny("n"), EBAny("b")])])
        self.assertEqual(Sketch([SketchRule([], [])]), s1.simplify())


class ExpandSketchTest(unittest.TestCase):
    def test_bound_fill_in_expanded(self):
        bound_dict = {"n_n": (0, 2), "n_m": (0, 2), "n_o": (1, 3)}
        sketch = Sketch(
            [SketchRule([CGreater('n_n')], [EDecr('n_n')]), SketchRule([CPositive('b_a')], [ENegative('b_a')])])

        exp_sketch = sketch.expand(bound_dict)

        wanted_exp_sketch = ExpandedSketch([ExpandedRule([NumericalVar('n_n', 1, "=")], [NumericalVar('n_n', 1, "<")]),
                                            ExpandedRule([NumericalVar('n_n', 2, "=")], [NumericalVar('n_n', 2, "<")]),
                                            ExpandedRule([BooleanVar('b_a', True, "=")],
                                                         [BooleanVar('b_a', False, "=")])
                                            ])

        # for e, r in enumerate(ltl_sketch.rules):
        #     print(e, r.conditions.show(), r.effects.show())
        for r1, r2 in zip(exp_sketch.rules, wanted_exp_sketch.rules):
            self.assertEqual(r1.conditions, r2.conditions)
            self.assertEqual(r1.effects, r2.effects)

        sketch_2 = Sketch([SketchRule([CZero('n_n')], [EDecr('n_o')])])
        exp_sketch_2 = sketch_2.expand(bound_dict)

        wanted_exp_sketch_2 = ExpandedSketch([
            ExpandedRule([NumericalVar('n_n', 0, "="), NumericalVar('n_o', 1, "=")], [NumericalVar('n_o', 1, "<")]),
            ExpandedRule([NumericalVar('n_n', 0, "="), NumericalVar('n_o', 2, "=")], [NumericalVar('n_o', 2, "<")]),
            ExpandedRule([NumericalVar('n_n', 0, "="), NumericalVar('n_o', 3, "=")], [NumericalVar('n_o', 3, "<")]),
        ])

        # for e, r in enumerate(ltl_sketch_2.rules):
        #     print(e, r.conditions.show(), '\t',  r.effects.show())

        for r1, r2 in zip(exp_sketch_2.rules, wanted_exp_sketch_2.rules):
            self.assertEqual(r1.conditions, r2.conditions)
            self.assertEqual(r1.effects, r2.effects)

        sketch_3 = Sketch([SketchRule([CGreater('n_n')], [EPositive('b_a')])])
        wanted_3 = ExpandedSketch([ExpandedRule([NumericalVar(data='n_n', value=0, operator='>')],
                                                [BooleanVar(data='b_a', value=True, operator='=')])])
        for r1, r2 in zip(sketch_3.expand(bound_dict).rules, wanted_3.rules):
            self.assertEqual(r1.conditions, r2.conditions)
            self.assertEqual(r1.effects, r2.effects)

        sketch_4 = Sketch([SketchRule([CNegative('b_a')], [EBEqual('b_a')])])
        wanted_4 = ExpandedSketch([ExpandedRule([BooleanVar(data='b_a', value=False, operator='=')],
                                                [BooleanVar(data='b_a', value=False, operator='=')])])

        for r1, r2 in zip(sketch_4.expand(bound_dict).rules, wanted_4.rules):
            self.assertEqual(r1.conditions, r2.conditions)
            self.assertEqual(r1.effects, r2.effects)

        sketch_no_cond = Sketch([SketchRule([], [EPositive('b_a')])])
        wanted_no_cond = ExpandedSketch([ExpandedRule([],
                                                      [BooleanVar(data='b_a', value=True, operator='=')])])

        for r1, r2 in zip(sketch_no_cond.expand(bound_dict).rules, wanted_no_cond.rules):
            self.assertEqual(r1.conditions, r2.conditions)
            self.assertEqual(r1.effects, r2.effects)

        sketch_any_cond = Sketch([SketchRule([CNAny('n_n')], [EPositive('b_a')])])
        wanted_any_cond = ExpandedSketch([ExpandedRule([],
                                                       [BooleanVar(data='b_a', value=True, operator='=')])])

        for r1, r2 in zip(sketch_any_cond.expand(bound_dict).rules, wanted_any_cond.rules):
            self.assertEqual(r1.conditions, r2.conditions)
            self.assertEqual(r1.effects, r2.effects)

        sketch_gr_cond = Sketch([SketchRule([CGreater('n_n')], [EPositive('b_a')])])
        wanted_gr_cond = ExpandedSketch([ExpandedRule([],
                                                      [BooleanVar(data='b_a', value=True, operator='=')])])

        for r in sketch_gr_cond.expand(bound_dict).rules:
            print(r.conditions, r.effects)

        for r1, r2 in zip(sketch_any_cond.expand(bound_dict).rules, wanted_any_cond.rules):
            self.assertEqual(r1.conditions, r2.conditions)
            self.assertEqual(r1.effects, r2.effects)

    def test_on_real_sketches(self):
        # TODO write these print statements in asserts once a method is constructed to compare sketches
        # delivery
        sketch_delivery_1 = Sketch([SketchRule([], [ENEqual("n_1"), EDecr("n_0")]),
                                    SketchRule([CGreater("n_0")], [EIncr("n_1")])])

        for e, r in enumerate(sketch_delivery_1.expand({"n_0": (1, 2), "n_1": (1, 2)}).rules):
            print("SketchRule(", r.conditions, r.effects, "), ")

        # gripper
        sketch_gripper_1 = Sketch([SketchRule([], [EDecr("n_1")]),
                                   SketchRule([], [EIncr("n_0"), ENEqual("n_1")])])
        print("gripper")
        for e, r in enumerate(sketch_gripper_1.expand({"n_0": (1, 2), "n_1": (1, 2)}).rules):
            print(e, r.conditions, r.effects)

        # blocks clear
        sketch_blocks_clear_0 = Sketch([
            SketchRule([CGreater("n")], [ENegative("b"), EDecr("n")]),
            SketchRule([], [EPositive("b"), ENEqual("n")])
        ])
        print("blocks clear")
        for e, r, in enumerate(sketch_blocks_clear_0.expand({"n": (1, 2)}).rules):
            print(e, r.conditions, r.effects)


class FromDLPlanTest(unittest.TestCase):
    def setUp(self) -> None:
        vocabulary_info = dlplan.core.VocabularyInfo()
        vocabulary_info.add_predicate("unary", 1)
        vocabulary_info.add_predicate("a", 1)
        vocabulary_info.add_predicate("b", 1)
        vocabulary_info.add_predicate("c", 1)
        factory = dlplan.core.SyntacticElementFactory(vocabulary_info)
        self.a = factory.parse_boolean("b_empty(c_primitive(a,0))")
        self.b = factory.parse_boolean("b_empty(c_primitive(b,0))")
        self.c = factory.parse_boolean("b_empty(c_primitive(c,0))")
        self.d = factory.parse_boolean("b_empty(c_primitive(unary,0))")
        self.e = factory.parse_boolean("b_empty(c_primitive(unary,0))")
        self.h = factory.parse_boolean("b_empty(c_primitive(unary,0))")

        self.n = factory.parse_numerical("n_count(c_primitive(unary,0))")
        self.m = factory.parse_numerical("n_count(c_not(c_primitive(unary,0)))")
        self.o = factory.parse_numerical("n_count(c_primitive(unary,0))")

    def test_rule_from_dlplan(self):
        builder = dlpolicy.PolicyBuilder()

        # {a} -> {a}
        c_pos_a = builder.add_pos_condition(self.a)
        e_pos_a = builder.add_pos_effect(self.a)
        rule1 = builder.add_rule({c_pos_a}, {e_pos_a})

        self.assertEqual(SketchRule([CPositive(self.a.compute_repr())],
                                    [EPositive(self.a.compute_repr())]),
                         SketchRule.from_dlplan_rule(rule1))

        # {n>0, m=0} -> {n incr, m↓}
        c_greater_n = builder.add_gt_condition(self.n)
        c_zero_n = builder.add_eq_condition(self.m)
        e_incr_n = builder.add_inc_effect(self.n)
        e_decr_n = builder.add_dec_effect(self.m)
        rule2 = builder.add_rule({c_greater_n, c_zero_n}, {e_incr_n, e_decr_n})

        # Compare conditions
        self.assertSetEqual({CGreater(self.n.compute_repr()), CZero(self.m.compute_repr())},
                            set(SketchRule.from_dlplan_rule(rule2).conditions))

        # Compare effects
        self.assertSetEqual({EIncr(self.n.compute_repr()), EDecr(self.m.compute_repr())},
                            set(SketchRule.from_dlplan_rule(rule2).effects))

        # {} -> {a=, n=}
        e_any_a = builder.add_bot_effect(self.a)
        e_any_n = builder.add_bot_effect(self.n)
        rule3 = builder.add_rule(set(), {e_any_a, e_any_n})

        self.assertSetEqual(set(),
                            set(SketchRule.from_dlplan_rule(rule3).conditions))

        self.assertEqual({EBEqual(self.a.compute_repr()), ENEqual(self.n.compute_repr())},
                         set(SketchRule.from_dlplan_rule(rule3).effects))

    def test_sketch_from_dlplan(self):
        builder = dlpolicy.PolicyBuilder()

        # empty policy
        empty_pol = builder.add_policy(set())
        self.assertEqual(Sketch([]), Sketch.from_policy(empty_pol))

        # {a -> ¬a, ¬b -> b}
        c_pos_a = builder.add_pos_condition(self.a)
        e_neg_a = builder.add_neg_effect(self.a)
        c_neg_b = builder.add_neg_condition(self.b)
        e_pos_b = builder.add_pos_effect(self.b)

        r1 = builder.add_rule({c_pos_a}, {e_neg_a})
        r2 = builder.add_rule({c_neg_b}, {e_pos_b})

        policy = builder.add_policy({r1, r2})

        # Rules can be in different order, so we check both orders. We cannot use sets to test this because SketchRules
        # are not hashable. This would not work with sketchrules that have multiple feature conditions or feature
        # effects since they can also be in a different order. A solution would be to use sets instead of lists in
        # the Sketch and SketchRule classes, but some "unhashable" errors need to be fixed then. For now, we already
        # tested getting SketchRules with multiple feature conditions and effects in the previous test, so we consider
        # this tested
        self.assertIn(Sketch.from_policy(policy).rules,
                      [[SketchRule([CPositive(self.a.compute_repr())], [ENegative(self.a.compute_repr())]),
                        SketchRule([CNegative(self.b.compute_repr())], [EPositive(self.b.compute_repr())])],
                       [SketchRule([CNegative(self.b.compute_repr())], [EPositive(self.b.compute_repr())]),
                        SketchRule([CPositive(self.a.compute_repr())], [ENegative(self.a.compute_repr())])]])


if __name__ == '__main__':
    unittest.main()
