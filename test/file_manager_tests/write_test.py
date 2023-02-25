import unittest

import json

import dlplan

import src
import src.file_manager as fm
from src.transition_system.graph import DirectedGraph
import src.transition_system as ts


class TransitionSystem(unittest.TestCase):
    def test_transition_system(self):
        file = "test/generated/transition_system.json"
        adj = [[[1], ["01"]], [[2], ["12"]], [[3], ["23"]], [[0], ["30"]]]
        init = 1
        goal = [2, 3]
        fm.write.transition_system(DirectedGraph(adj), init, goal, file)

        with open(file, 'r') as f:
            data = json.load(f)

        self.assertEqual(data,
                         {'goal': [2, 3],
                          'graph': [[[1], ['01']], [[2], ['12']], [[3], ['23']], [[0], ['30']]],
                          'init': 1})

        rgraph, rinit, rgoal = fm.read.transition_system(file)
        self.assertEqual(rgraph.adj, adj)
        self.assertEqual(rinit, init)
        self.assertEqual(rgoal, goal)


class States(unittest.TestCase):
    def setUp(self) -> None:
        domain_path: str = "gripper/domain.pddl"
        domain = src.transition_system.tarski.load_domain(domain_path)
        instance_path: str = "gripper_test/p-1-0.pddl"

        iproblem = ts.tarski.load_instance(domain_path, instance_path)
        self.instance = ts.conversions.dlinstance_from_tarski(domain, iproblem)
        self.factory = dlplan.SyntacticElementFactory(self.instance.get_vocabulary_info())

        tarski_system: ts.tarski.TarskiTransitionSystem = ts.tarski.from_instance(iproblem)
        self.dl_system: ts.dlplan.DLTransitionModel = ts.conversions.tarski_to_dl_system(tarski_system, self.instance)

        self.states = self.dl_system.states

        self.b1 = "b_empty(c_and(c_one_of(rooma),c_primitive(at-robby,0)))"
        self.n1 = "n_count(c_primitive(carry,0))"

    def test_write_states(self):
        fm.write.dl_states(self.states, "test/generated/states.json")

        with open("test/generated/states.json", 'r') as f:
            data = json.load(f)

        self.assertEqual(list(map(lambda x: set(x), data)),
                         list(map(lambda x: set(x), [["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(right)", "free(left)", "at(ball1,rooma)", "at-robby(rooma)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(right)", "free(left)", "at(ball1,rooma)", "at-robby(roomb)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(right)", "at-robby(rooma)", "carry(ball1,left)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(left)", "at-robby(rooma)", "carry(ball1,right)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(left)", "at-robby(roomb)", "carry(ball1,right)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(right)", "free(left)", "at(ball1,roomb)", "at-robby(roomb)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(right)", "free(left)", "at(ball1,roomb)", "at-robby(rooma)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(right)", "at-robby(roomb)", "carry(ball1,left)"]])))

        rstates = fm.read.dl_states("test/generated/states.json", self.instance)
        for s, rs in zip(self.states, rstates):
            self.assertEqual(s, rs)

    def test_feature_reprs(self):
        fm.write.feature_representations(["b_empty(c_and(c_one_of(rooma),c_primitive(at-robby,0)))", "n_count(c_primitive(carry,0))"], "test/generated/feature_reps")
        with open("test/generated/feature_reps", 'r') as f:
            data = json.load(f)

        self.assertEqual(data, ["b_empty(c_and(c_one_of(rooma),c_primitive(at-robby,0)))", "n_count(c_primitive(carry,0))"])

    def test_features(self):
        b1 = self.factory.parse_boolean(self.b1)
        n1 = self.factory.parse_numerical(self.n1)
        fm.write.features([b1, n1], "test/generated/features")

        with open("test/generated/features", 'r') as f:
            data = json.load(f)

        self.assertEqual(data, [self.b1, self.n1])



if __name__ == '__main__':
    unittest.main()
