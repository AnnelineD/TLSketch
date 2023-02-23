import unittest

import json
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


class States(unittest.TestCase):
    def test_states(self):
        domain_path: str = "gripper/domain.pddl"
        domain = src.transition_system.tarski.load_domain(domain_path)
        instance_path: str = "gripper_test/p-1-0.pddl"

        iproblem = ts.tarski.load_instance(domain_path, instance_path)
        instance = ts.conversions.dlinstance_from_tarski(domain, iproblem)

        tarski_system: ts.tarski.TarskiTransitionSystem = ts.tarski.from_instance(iproblem)
        dl_system: ts.dlplan.DLTransitionModel = ts.conversions.tarski_to_dl_system(tarski_system, instance)

        states = dl_system.states
        fm.write.dl_states(states, "test/generated/states.json")

        with open("test/generated/states.json", 'r') as f:
            data = json.load(f)

        self.assertEqual(data,
                         [["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(right)", "free(left)", "at(ball1,rooma)", "at-robby(rooma)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(right)", "free(left)", "at(ball1,rooma)", "at-robby(roomb)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(right)", "at-robby(rooma)", "carry(ball1,left)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(left)", "at-robby(rooma)", "carry(ball1,right)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(left)", "at-robby(roomb)", "carry(ball1,right)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(right)", "free(left)", "at(ball1,roomb)", "at-robby(roomb)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(right)", "free(left)", "at(ball1,roomb)", "at-robby(rooma)"], ["room(rooma)", "room(roomb)", "gripper(right)", "gripper(left)", "ball(ball1)", "free(right)", "at-robby(roomb)", "carry(ball1,left)"]])

        # states = read_states(instance, "data/state_files/gripper_test/p-1-0.json")
        # for i, state in enumerate(states):
        #     print(i, [instance.get_atom(idx) for idx in state.get_atom_idxs()])



if __name__ == '__main__':
    unittest.main()
