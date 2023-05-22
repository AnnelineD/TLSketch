import os
from functools import reduce
from typing import Iterator
import json

import dlplan
import ltl
from math import comb
import pynusmv
import tarski.fstrips
from tqdm import tqdm

import src.transition_system.tarski
from examples import *
from src.logics.conditions_effects import Condition, Effect, CNAny, EIncr, EDecr, ENEqual
from src.logics.rules import LTLSketch, Sketch, SketchRule

from src.sketch_verification import verify_sketch, law1, law2, law3
from src.sketch_verification.feature_instance import FeatureInstance
from src.sketch_verification.laws import law_test, exists, if_followed_next_law, simple_law
from src.sketch_verification.verify import check_file
from src.to_smv.conversion import *
from src.to_smv.make_smv import to_smv_format
#from src.logics.sketch_to_ltl import policy_to_arrowsketch, fill_in_rule, fill_in_rules, list_to_ruletups, \
#    ruletups_to_arrowsketch

import src.file_manager as fm
from src.dlplan_utils import parse_features
from src.transition_system.transition_system import TransitionSystem


def show_domain_info():
    domain = Miconic()
    print(domain.dl_system.graph.show())
    print(domain.dl_system.graph.adj)

    print(domain)

    sketch = domain.sketch_2()
    print("sketch", sketch)
    print()
    f_domain = domain.dl_system.add_features(sketch.get_boolean_features() + sketch.get_numerical_features())
    arrow_sketch = policy_to_arrowsketch(sketch)
    print("features: ", f_domain.features.keys())
    print("arrow sketch:", arrow_sketch.show())

    print("bounds:", f_domain.get_feature_bounds())
    ltl_rules = fill_in_rules(arrow_sketch.rules, f_domain.get_feature_bounds())
    goal_atoms = domain.dl_system.instance_info.get_static_atoms()
    print("goal atoms", goal_atoms)
    for i, s in enumerate(domain.dl_system.states):
        print(i, s)
    print()
    print("smv:")
    print("MODULE main")
    print(transition_system_to_smv(domain.dl_system))
    print(features_to_smv(f_domain))
    ltl_sketch = LTLSketch(ltl_rules)
    for r in ltl_sketch.rules:
        print(r.show())

def main():
    domain = Gripper()
    sketch = domain.sketch_1()
    print("sketch", sketch)
    arrow_sketch = policy_to_arrowsketch(sketch)
    print(arrow_sketch.show())
    f_domain = domain.dl_system.add_features(sketch.get_boolean_features() + sketch.get_numerical_features())
    ltl_rules = fill_in_rules(arrow_sketch.rules, f_domain.get_feature_bounds())
    for r in ltl_rules:
        print(r.show())






def test_pysmv():
    pynusmv.init.init_nusmv()
    pynusmv.glob.load_from_file("test/sketch_verification/blocks_clear_0.smv")
    pynusmv.glob.compute_model()
    spec = pynusmv.prop.x(pynusmv.prop.atom("state = s2"))
    for p in pynusmv.glob.prop_database():
        print(pynusmv.mc.check_ltl_spec(p.expr), p.expr)
    pynusmv.init.deinit_nusmv()

def test_made_sketch_gripper():
    sketch = Sketch([SketchRule([CNAny(feature='n_count(c_equal(r_primitive(at,0,1),r_primitive(at_g,0,1)))')],
                                [EIncr(feature='n_count(c_equal(r_primitive(at,0,1),r_primitive(at_g,0,1)))')])])

    with open("cache/gripper-strips/transition_systems/rooma_roomb_left_right_ball1_ball2_ball3_(at(ball1,roomb)andat(ball2,roomb)andat(ball3,roomb)).json", "r") as f:
        transition_sys = TransitionSystem.deserialize(json.load(f))
    with open("cache/gripper-strips/features/5_5_10_10_10_180_100000_1/rooma_roomb_left_right_ball1_ball2_ball3_[at_g(ball1,roomb),at_g(ball2,roomb),at_g(ball3,roomb)].json", "r") as f:
        feature_vals = json.load(f)
    #print(transition_sys.graph.show())
    inst = FeatureInstance(transition_sys.graph, transition_sys.init, transition_sys.goals, feature_vals)
    return verify_sketch(sketch, inst, [law3])

def test_Drexler_sketch_gripper():
    width_1 = '(:policy (:boolean_features) (:numerical_features "n_count(c_primitive(at,0))" "n_count(c_some(r_primitive(at,0,1),c_one_of(rooma)))") (:rule (:conditions) (:effects (:e_n_dec 1)))(:rule (:conditions) (:effects (:e_n_bot 1) (:e_n_inc 0))))'

    sketch = Sketch([SketchRule([],
                                [EDecr(feature='n_count(c_some(r_primitive(at,0,1),c_one_of(rooma)))')]),
                     SketchRule([],
                                [EIncr(feature='n_count(c_primitive(at,0))'), ENEqual('n_count(c_some(r_primitive(at,0,1),c_one_of(rooma)))')])])

    with open("cache/gripper-strips/transition_systems/rooma_roomb_left_right_ball1_ball2_ball3_(at(ball1,roomb)andat(ball2,roomb)andat(ball3,roomb)).json", "r") as f:
        transition_sys = TransitionSystem.deserialize(json.load(f))
    with open("cache/gripper-strips/features/5_5_10_10_10_180_100000_1/rooma_roomb_left_right_ball1_ball2_ball3_[at_g(ball1,roomb),at_g(ball2,roomb),at_g(ball3,roomb)].json", "r") as f:
        feature_vals = json.load(f)
    #print(transition_sys.graph.show())
    inst = FeatureInstance(transition_sys.graph, transition_sys.init, transition_sys.goals, feature_vals)
    return verify_sketch(sketch, inst, [law1, law2, simple_law])

def filter_rules():
    with open("generated/gripper/two_instances_simple_laws_5_5_10_10_10_180_100000_1_2_1.json") as f:
        sketches_2 = [Sketch.deserialize(rs) for rs in json.load(f)]

    with open("generated/gripper/two_instances_simple_laws_5_5_10_10_10_180_100000_1_1_1.json") as f:
        sketches_1: list[Sketch] = [Sketch.deserialize(rs) for rs in json.load(f)]

    filtered = filter(lambda sk: not any(rs_1 in sk.rules for sk_1 in sketches_1 for rs_1 in sk_1.rules), sketches_2)
    for f in filtered:
        print(f.serialize())
        print('\n')


if __name__ == '__main__':
    #print(test_sketch())
    #law = law_test.expand(7)
    #ex = exists.expand(7)
    #if_followed = if_followed_next_law.expand(7)
    #simple = simple_law.expand(7)
    #print(check_file("gripper3.smv", [simple]))

    test_Drexler_sketch_gripper()

    """
    sketches = list(model_check_from_files("gripper_test"))
    for s in sketches:
        print(s.show())

    print()
    
    sketches_ = list(model_check_sketches_bis())
    for s in sketches_:
        print(s.show())
    """
    #test_read_states()

    """
    from pynusmv import prop

    pynusmv.init.init_nusmv()
    pynusmv.glob.load_from_file(filepath="blocks_clear_0.smv")
    pynusmv.glob.compute_model()
    fsm = pynusmv.glob.prop_database().master.bddFsm
    for state in fsm.pick_all_states(fsm.init):
        print(state.get_str_values())



    def y(spec):
        if spec is None:
            raise ValueError()
        # freeit=True seems to be erroneous
        s = prop.Spec(pynusmv.node.nsnode.find_node(pynusmv.parser.nsparser.OP_PREC, spec._ptr, None), freeit=False)
        s._car = spec
        return s

    spec = prop.x(y(prop.true() & prop.true()))
    print(pynusmv.mc.check_ltl_spec(spec))
    """

