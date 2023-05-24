import unittest

import ltl
import src.transition_system as ts
from src.logics.conditions_effects import CPositive
from src.logics.rules import LTLRule
from src.sketch_verification.feature_instance import FeatureInstance
from src.to_smv.conversion import *
from src.to_smv.make_smv import to_smv_format


class SMVTest(unittest.TestCase):
    def setUp(self) -> None:
        self.g = DirectedGraph()
        n0 = self.g.grow()
        n1 = self.g.grow()
        self.g.add(n0, n1, "lower")
        self.g.add(n1, n0, "raise")

        self.sketch = LTLSketch([LTLRule(BooleanVar("b0", True), ltl.Or(NumericalVar("n0", 0), NumericalVar("n0", 1)))])

    def test_to_smv_format(self):
        smv = """MODULE main
VAR 
  state: {s0, s1};
ASSIGN 
  init(state) := s0; 
  next(state) := case 
          state = s0: {s1};
          state = s1: {s0};
                 esac;
DEFINE 
  	b0 := case 
		state = s0: FALSE;
		state = s1: TRUE; 
	esac;
 	n0 := case 
		state = s0: 0;
		state = s1: 1; 
	esac;
	goal := state in {s0, s1};
	c0 := b0=TRUE; 
 	e0 := (n0=0 | n0=1);
"""
        smv_option_2 = """MODULE main
VAR 
  state: {s0, s1};
ASSIGN 
  init(state) := s0; 
  next(state) := case 
          state = s0: {s1};
          state = s1: {s0};
                 esac;
DEFINE 
  	n0 := case 
		state = s0: 0;
		state = s1: 1; 
	esac;
 	b0 := case 
		state = s0: FALSE;
		state = s1: TRUE; 
	esac;
	goal := state in {s0, s1};
	c0 := b0=TRUE; 
 	e0 := (n0=0 | n0=1);
"""
        # print(to_smv_format(FeatureInstance(self.g, 0, [0, 1], {"n0": [0, 1], "b0": {False, True}}), self.sketch))
        # self.assertEqual(smv, to_smv_format(FeatureInstance(self.g, 0, [0, 1], {"n0": [0, 1], "b0": {False, True}}), self.sketch))
        self.assertIn(to_smv_format(FeatureInstance(self.g, 0, [0, 1], {"n0": [0, 1], "b0": {False, True}}), self.sketch), [smv, smv_option_2])


class ToSMVComponentsTest(unittest.TestCase):

    def test_graph_to_smv(self):
        g = DirectedGraph()
        n0 = g.grow()
        n1 = g.grow()
        g.add(n0, n1, "lower")
        g.add(n1, n0, "raise")

        # print(graph_to_smv(g, 0))
        smv_var = """VAR 
  state: {s0, s1};
ASSIGN 
  init(state) := s0; 
  next(state) := case 
          state = s0: {s1};
          state = s1: {s0};
                 esac;"""

        self.assertEqual(smv_var, graph_to_smv(g, 0))

    def test_features_to_smv(self):
        smv_features = """DEFINE 
  	b := case 
		state = s0: TRUE;
		state = s1: FALSE; 
	esac;
	goal := state in {s1};"""

        self.assertEqual(smv_features, valuations_to_smv({"b": [True, False]}, [1], {"b"}))

if __name__ == '__main__':
    unittest.main()
