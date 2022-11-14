import unittest

from src.transition_system.dl_transition_model import *


class DLTransitionModelTest(unittest.TestCase):
    v = dlplan.VocabularyInfo()
    v.add_predicate("on", 2)
    v.add_predicate("on_g", 2)
    v.add_predicate("ontable", 1)
    v.add_predicate("holding", 1)
    v.add_predicate("clear", 1)
    v.add_predicate("arm-empty", 0)

    i = dlplan.InstanceInfo(v)
    i.add_atom("on", ["a", "b"])
    i.add_atom("on", ["b", "a"])
    i.add_atom("ontable", ["a"])
    i.add_atom("ontable", ["b"])
    i.add_atom("holding", ["a"])
    i.add_atom("holding", ["b"])
    i.add_atom("clear", ["a"])
    i.add_atom("clear", ["b"])
    i.add_atom("arm-empty", [])

    atoms = i.get_atoms()
    a0 = atoms[0]
    a1 = atoms[1]
    a2 = atoms[2]
    a3 = atoms[3]
    a4 = atoms[4]
    a5 = atoms[5]
    a6 = atoms[6]
    a7 = atoms[7]
    a8 = atoms[8]
    s0 = dlplan.State(i, [a0, a3, a6, a8])
    s1 = dlplan.State(i, [a1, a2, a7, a8])
    s2 = dlplan.State(i, [a2, a3, a6, a7, a8])
    s3 = dlplan.State(i, [a3, a4, a7])
    s4 = dlplan.State(i, [a2, a5, a6])
    states = {s0, s1, s2, s3, s4}

    tm = DLTransitionModel(i, states)

    f = dlplan.SyntacticElementFactory(v)
    n_feature: dlplan.Numerical = f.parse_numerical("n_count(c_primitive(clear,0))")
    n_feature.set_index(0)
    b_feature = f.parse_boolean("b_empty(c_primitive(holding,0))")
    b_feature.set_index(0)

    def test_something(self):

        # bool_tm = add_feature_propositions(self.tm, self.b_feature)
        bool_tm = add_features2(self.tm, [self.b_feature])
        print(bool_tm.states)



if __name__ == '__main__':
    unittest.main()
