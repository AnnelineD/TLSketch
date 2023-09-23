import unittest

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


if __name__ == '__main__':
    unittest.main()
