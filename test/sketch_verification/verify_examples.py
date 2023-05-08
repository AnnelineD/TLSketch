import unittest
from functools import reduce

import ctl

from src.logics.laws import AbstractLaw
from src.logics.rules import Sketch
from src.sketch_verification.feature_instance import FeatureInstance
from src.sketch_verification.verify import verify_sketch
from examples import *
import src.file_manager as fm


class VerifyExamples(unittest.TestCase):

    def test_verify_sketch(self):
        print("yes")

        sketch = Sketch.from_policy(BlocksClear().sketch_2())
        instance = fm.read.feature_instance("test/sketch_verification/ts_blocks_clear_p-3-0.json", "test/sketch_verification/f_blocks_clear_p-3-0.json")

        def ctl_rule_can_be_followed(n_rules: int) -> ctl.CTLFormula:
            ctl_conditions = [ctl.Var(f'c{i}') for i in range(n_rules)]
            ctl_effects = [ctl.Var(f'e{i}') for i in range(n_rules)]
            ctl_rules = list(zip(ctl_conditions, ctl_effects))
            ctl_goal = ctl.Var('goal')
            return ctl.AG(ctl.Or(ctl.Or(reduce(ctl.Or, [ctl.And(c, ctl.EF(ctl.And(e, ctl.EF(ctl_goal)))) for c, e in ctl_rules]), ctl_goal), ctl.Not(ctl.EF(ctl_goal))))

        abstr_law = AbstractLaw(ctl_rule_can_be_followed, True)

        self.assertTrue(verify_sketch(sketch, instance, [abstr_law]))


if __name__ == '__main__':
    unittest.main()
