import unittest

from src.logics.conditions_effects import CGreater, ENAny, CPositive, ENegative
from src.logics.rules import SketchRule, Sketch


class SketchSavingTest(unittest.TestCase):
    def test_sketch_rule(self):
        sr = SketchRule([CGreater("f1")], [ENAny("f2")])
        serialized = sr.serialize()
        deserialized = SketchRule.deserialize(serialized)

        self.assertEqual(sr, deserialized)

    def test_sketch(self):
        sketch = Sketch([SketchRule([CGreater("f1")], [ENAny("f2")]),
                         SketchRule([CPositive("f3")], [ENegative("f4")])])

        serialized = sketch.serialize()
        deserialized = Sketch.deserialize(serialized)

        self.assertEqual(sketch, deserialized)


if __name__ == '__main__':
    unittest.main()
