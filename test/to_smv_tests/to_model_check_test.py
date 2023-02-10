import unittest

import dlplan

from src.to_smv.conversion import *
from src.transition_system.graph import DirectedGraph


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        v = dlplan.VocabularyInfo()
        v.add_predicate("raise", 0)

        i = dlplan.InstanceInfo(v)
        i.add_atom("raise", [])

        atoms = i.get_atoms()
        a0 = atoms[0]

        s0 = dlplan.State(i, [a0])
        s1 = dlplan.State(i, [])

        states = [s0, s1]
        g = DirectedGraph()
        n0 = g.grow()
        n1 = g.grow()
        g.add(n0, n1, "lower")
        g.add(n1, n0, "raise")

        self.tm = DLTransitionModel(i, states, 0, [], g)

        f = dlplan.SyntacticElementFactory(v)
        b_feature = f.parse_boolean("b_nullary(raise))")
        b_feature.set_index(0)

        self.ftm = self.tm.add_features([b_feature])
        print(self.ftm.features)


    def test_something(self):
        print(transition_system_to_smv(self.tm))
        print(features_to_smv(self.ftm))
        smv_var = """VAR 
  state: {s0, s1};
ASSIGN 
  init(state) := s0; 
  next(state) := case 
          state = s0: {s1};
          state = s1: {s0};
                 esac;"""
        smv_features = """DEFINE 
  	b0 := case 
		state = s0: TRUE;
		state = s1: FALSE; 
	esac;"""
        self.assertEqual(smv_var, transition_system_to_smv(self.tm))
        self.assertEqual(smv_features, features_to_smv(self.ftm))


if __name__ == '__main__':
    unittest.main()
