import unittest

from src.logics.conditions_effects import *
from src.logics.rules import Sketch, SketchRule


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

        s_1 = Sketch.deserialize([[[], ["EIncr(feature='n_count(c_equal(r_primitive(on,0,1),r_primitive(on_g,0,1)))')", "EPositive(feature='b_nullary(arm-empty)')"]]])
        s_2 = Sketch.deserialize([[[], ["EIncr(feature='n_count(c_equal(r_primitive(on,0,1),r_primitive(on_g,0,1)))')", "EPositive(feature='b_nullary(arm-empty)')"]], [[], ["EIncr(feature='n_count(c_equal(r_primitive(on,0,1),r_primitive(on_g,0,1)))')", "ENegative(feature='b_nullary(arm-empty)')"]]])
        print(s_2.contains_sketch(s_1))

        past_sketches = [s_1]
        candidate_sketches = [s_2, Sketch.deserialize([[[],["EIncr(feature='f')"]]])]
        filtered_candidate_sketches = filter(lambda s2: not (any(s2.contains_sketch(s1) for s1 in past_sketches)),
                                             candidate_sketches)

        print(list(filtered_candidate_sketches))

    def test_simplify(self):
        s1 = Sketch([SketchRule([CNAny("n"), CBAny("b")], [ENAny("n"), EBAny("b")])])
        print(s1.simplify())


if __name__ == '__main__':
    unittest.main()
