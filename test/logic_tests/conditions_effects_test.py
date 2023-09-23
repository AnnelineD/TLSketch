import unittest
from src.logics.conditions_effects import *
import dlplan
import dlplan.policy


class ConditionsTest(unittest.TestCase):
    def setUp(self) -> None:
        # make one of each different condition
        self.cp = CPositive("b")
        self.cn = CNegative("b")
        self.cba = CBAny("b")

        self.cg = CGreater("n")
        self.cz = CZero("n")
        self.cna = CNAny("n")

        # make for each different condition a dlplan version
        vocabulary_info = dlplan.core.VocabularyInfo()
        vocabulary_info.add_predicate("unary", 1, False)

        factory = dlplan.core.SyntacticElementFactory(vocabulary_info)
        self.b_str = "b_empty(c_primitive(unary,0))"
        self.n_str = "n_count(c_primitive(unary,0))"
        b = factory.parse_boolean(self.b_str)
        n = factory.parse_numerical(self.n_str)

        builder = dlplan.policy.PolicyBuilder()
        self.dlplan_cn = builder.add_neg_condition(b)     # con: ¬b
        self.dlplan_cp = builder.add_pos_condition(b)     # con: b
        self.dlplan_cg = builder.add_gt_condition(n)       # con: n>0
        self.dlplan_cz = builder.add_eq_condition(n)       # con: n=0

    def test_types(self):
        self.assertTrue(isinstance(self.cp, Condition))
        self.assertTrue(isinstance(self.cp, BooleanCondition))
        self.assertTrue(isinstance(self.cp, CPositive))

    def test_equality(self):
        self.assertEqual(self.cp, CPositive("b"))

        self.assertNotEqual(self.cp, CNegative("b"))
        self.assertNotEqual(self.cp, CPositive("n"))

    def test_show(self):
        # no feature labels
        self.assertEqual("bb", self.cp.show())
        self.assertEqual("¬bb", self.cn.show())
        self.assertEqual("", self.cba.show())

        self.assertEqual("nn>0", self.cg.show())
        self.assertEqual("nn=0", self.cz.show())
        self.assertEqual("", self.cna.show())

        # feature labels
        self.assertEqual("bb0", self.cp.show({"b": "b0"}))
        self.assertEqual("¬btest", self.cn.show({"b": "test", "n": "something else", "z": "another thing"}))
        self.assertEqual("", self.cba.show({"b": "012"}))

        self.assertEqual("nn0>0", self.cg.show({"n": "n0"}))
        self.assertEqual("ntest=0", self.cz.show({"b": "something else", "n": "test", "z": "another thing"}))
        self.assertEqual("", self.cna.show({"b": "test", "n": "something else", "z": "another thing"}))

    def test_from_dlplan(self):
        self.assertEqual(CPositive(self.b_str), Condition.from_dlplan(self.dlplan_cp))
        self.assertEqual(CNegative(self.b_str), Condition.from_dlplan(self.dlplan_cn))
        self.assertEqual(CGreater(self.n_str), Condition.from_dlplan(self.dlplan_cg))
        self.assertEqual(CZero(self.n_str), Condition.from_dlplan(self.dlplan_cz))

        self.assertNotEqual(CPositive(self.n_str), Condition.from_dlplan(self.dlplan_cp))

    def test_invert(self):
        self.assertEqual(self.cn, self.cp.invert())
        self.assertEqual(self.cp, self.cn.invert())
        self.assertEqual(self.cz, self.cg.invert())
        self.assertEqual(self.cg, self.cz.invert())


class EffectsTest(unittest.TestCase):
    def setUp(self) -> None:
        # make one of each different condition
        self.ep = EPositive("b")
        self.en = ENegative("b")
        self.eba = EBAny("b")
        self.ebe = EBEqual("b")

        self.ei = EIncr("n")
        self.ed = EDecr("n")
        self.ena = ENAny("n")
        self.ene = ENEqual("n")

        # make for each different condition a dlplan version
        vocabulary_info = dlplan.core.VocabularyInfo()
        vocabulary_info.add_predicate("unary", 1, False)

        factory = dlplan.core.SyntacticElementFactory(vocabulary_info)
        self.b_str = "b_empty(c_primitive(unary,0))"
        self.n_str = "n_count(c_primitive(unary,0))"
        b = factory.parse_boolean(self.b_str)
        n = factory.parse_numerical(self.n_str)

        builder = dlplan.policy.PolicyBuilder()
        self.dlplan_ep = builder.add_pos_effect(b)      # eff: b
        self.dlplan_en = builder.add_neg_effect(b)      # eff: ¬b
        self.dlplan_ebe = builder.add_bot_effect(b)     # eff: b=
        self.dlplan_ei = builder.add_inc_effect(n)      # eff: n
        self.dlplan_ed = builder.add_dec_effect(n)      # eff: n↓
        self.dlplan_ene = builder.add_bot_effect(n)     # eff: n=

    def test_types(self):
        self.assertTrue(isinstance(self.ep, Effect))
        self.assertTrue(isinstance(self.ep, BooleanEffect))
        self.assertTrue(isinstance(self.ep, EPositive))

        self.assertFalse(isinstance(self.ep, NumericalEffect))
        self.assertFalse(isinstance(self.ep, ENegative))

    def test_equality(self):
        self.assertEqual(self.ep, EPositive("b"))

        self.assertNotEqual(self.ep, ENegative("b"))
        self.assertNotEqual(self.ep, EPositive("n"))

    def test_show(self):
        # no feature labels
        self.assertEqual("bb", self.ep.show())
        self.assertEqual("¬bb", self.en.show())
        self.assertEqual("bb?", self.eba.show())
        self.assertEqual("bb=", self.ebe.show())

        self.assertEqual("nn↑", self.ei.show())
        self.assertEqual("nn↓", self.ed.show())
        self.assertEqual("nn?", self.ena.show())
        self.assertEqual("nn=", self.ene.show())

        # feature labels
        self.assertEqual("bb0", self.ep.show({"b": "b0"}))
        self.assertEqual("¬btest", self.en.show({"b": "test", "n": "something else", "z": "another thing"}))
        self.assertEqual("btest?", self.eba.show({"b": "test", "n": "something else", "z": "another thing"}))
        self.assertEqual("btest=", self.ebe.show({"b": "test", "n": "something else", "z": "another thing"}))

        self.assertEqual("nn0↑", self.ei.show({"n": "n0"}))
        self.assertEqual("ntest↓", self.ed.show({"b": "something else", "n": "test", "z": "another thing"}))
        self.assertEqual("ntest?", self.ena.show({"b": "something else", "n": "test", "z": "another thing"}))
        self.assertEqual("ntest=", self.ene.show({"b": "something else", "n": "test", "z": "another thing"}))

    def test_from_dlplan(self):
        self.assertEqual(EPositive(self.b_str), Effect.from_dlplan(self.dlplan_ep))
        self.assertEqual(ENegative(self.b_str), Effect.from_dlplan(self.dlplan_en))
        self.assertEqual(EBEqual(self.b_str), Effect.from_dlplan(self.dlplan_ebe))

        self.assertEqual(EIncr(self.n_str), Effect.from_dlplan(self.dlplan_ei))
        self.assertEqual(EDecr(self.n_str), Effect.from_dlplan(self.dlplan_ed))
        self.assertEqual(ENEqual(self.n_str), Effect.from_dlplan(self.dlplan_ene))

        self.assertNotEqual(EPositive(self.n_str), Effect.from_dlplan(self.dlplan_ep))


if __name__ == '__main__':
    unittest.main()
