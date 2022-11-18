import unittest

import dlplan

from src.transition_system.conversions import tarski_to_dl_system
from src.transition_system.dl_transition_model import DLTransitionModel
from src.transition_system.tarski_manipulation import get_tarski_domain_and_instance
from src.transition_system.tarski_transition_model import TarskiTransitionSystem
from src.to_model_checker.model_check_input import *


class MyTestCase(unittest.TestCase):

    def print_smv(self, domain_file, instance_file, sketch: str):
        d, i = get_tarski_domain_and_instance(domain_file, instance_file)
        tarski_ts = TarskiTransitionSystem(d, i)
        dl_ts = tarski_to_dl_system(tarski_ts)
        factory = dlplan.SyntacticElementFactory(dl_ts.instance_info.get_vocabulary_info())
        sketch: dlplan.Policy = dlplan.PolicyReader().read(sketch, factory)

        dl_ts_f = dl_ts.add_features(sketch.get_boolean_features() + sketch.get_numerical_features())
        print(dl_ts.states)
        print(convert_transition_system(dl_ts))
        print(convert_features(dl_ts_f))


    def test_blocks_clear(self):
        blocks_clear_domain = "../blocks_4_clear/domain.pddl"
        blocks_clear_instance = "../blocks_4_clear/p-3-0.pddl"
        sketch_0 = '(:policy\n'\
                    '(:boolean_features "b_nullary(arm-empty)")\n'\
                    '(:numerical_features "n_count(c_primitive(on,0))")\n'\
                    '(:rule (:conditions ) (:effects (:e_b_pos 0) (:e_n_bot 0)))\n'\
                    '(:rule (:conditions (:c_n_gt 0)) (:effects (:e_b_neg 0) (:e_n_dec 0)))\n'\
                    ')'
        self.print_smv(blocks_clear_domain, blocks_clear_instance, sketch_0)


if __name__ == '__main__':
    unittest.main()
