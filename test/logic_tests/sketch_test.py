import unittest

from src.logics.conditions_effects import CGreater, EDecr
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


if __name__ == '__main__':
    unittest.main()
