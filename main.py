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
from src.logics.conditions_effects import Condition, Effect
from src.logics.rules import LTLSketch
from src.sketch_generation.generation import generate_sketches, get_feature_sets, construct_feature_generator, \
    generate_rules, generate_sketches_from_rules
from src.to_smv.conversion import *
from src.to_smv.make_smv import to_smv_format
from src.logics.sketch_to_ltl import policy_to_arrowsketch, fill_in_rule, fill_in_rules, list_to_ruletups, \
    ruletups_to_arrowsketch
from src.logics.formula_generation import FormulaGenerator
from src.model_check.model_check import check_file, model_check_sketch


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

def make_smv():
    domain = BlocksOn()
    filename = "blocks_on_2.smv"
    print(domain.dl_system().graph.show())
    print(domain.dl_system().states)
    print(domain.dl_system().goal_states)
    print(domain.dl_system().instance_info.get_static_atoms())
    sketch = domain.sketch_2()
    arrow_sketch = policy_to_arrowsketch(sketch)
    f_domain = domain.dl_system().add_features(sketch.get_boolean_features() + sketch.get_numerical_features())
    ltl_rules = fill_in_rules(arrow_sketch.rules, f_domain.get_feature_bounds())
    g = FormulaGenerator(len(ltl_rules))
    with open(filename, 'w') as f:
        f.write("MODULE main\n")
        f.write(transition_system_to_smv(domain.dl_system()) + '\n')
        f.write(features_to_smv(f_domain) + '\n')
        f.write(rules_to_smv(ltl_rules) + '\n')
        f.write("LTLSPEC " + ltl_to_smv(g.one_condition()) + ";" + '\n')
        f.write("LTLSPEC " + ltl_to_smv(g.rules_followed_then_goal()) + ";" + '\n')
        f.write("LTLSPEC " + ltl_to_smv(g.there_exists_a_path()) + ";" + '\n')


def calculate_features_to_smv(boolean_features, numerical_features):
    domain = BlocksOn()
    filename = "blocks_on_2.smv"
    sketch = domain.sketch_2()
    arrow_sketch = policy_to_arrowsketch(sketch)
    nfs = [domain.factory().parse_numerical(n) for n in numerical_features]
    bfs = [domain.factory().parse_boolean(b) for b in boolean_features]
    f_domain = domain.dl_system().add_features(bfs + nfs)
    with open(filename, 'w') as f:
        f.write("MODULE main\n")
        f.write(transition_system_to_smv(domain.dl_system()) + '\n')
        f.write(features_to_smv(f_domain) + '\n')


def print_ltl():
    g = FormulaGenerator(4, 2)
    print("LTLSPEC " + ltl_to_smv(g.one_condition()))
    print("LTLSPEC " + ltl_to_smv(g.rules_followed_then_goal()))
    print("LTLSPEC " + ltl_to_smv(g.there_exists_a_path()))


def test_pysmv():
    pynusmv.init.init_nusmv()
    pynusmv.glob.load_from_file("blocks_clear_0.smv")
    pynusmv.glob.compute_model()
    spec = pynusmv.prop.x(pynusmv.prop.atom("state = s2"))
    for p in pynusmv.glob.prop_database():
        print(pynusmv.mc.check_ltl_spec(p.expr), p.expr)
    pynusmv.init.deinit_nusmv()


def model_check_sketches():
    domain = BlocksOn()
    directory = "smvs/"
    filename = "blocks_on_2.smv"
    real_sketch = domain.sketch_2()
    bs = real_sketch.get_boolean_features()
    ns = real_sketch.get_numerical_features()
    sketches = generate_sketches(bs, ns, 1)

    f_domain = domain.dl_system().add_features(bs + ns)
    for s in tqdm(sketches):
        # print(s)
        tups = list_to_ruletups(s)
        # print("t", tups)
        arrow_sketch = ruletups_to_arrowsketch(tups)
        # print("as", arrow_sketch.show())
        ltl_rules = fill_in_rules(arrow_sketch.rules, f_domain.get_feature_bounds())
        # print("ltl", ltl_rules)
        assert(len(ltl_rules) > 0)
        g = FormulaGenerator(len(ltl_rules))
        with open(directory + filename, 'w') as f:
            ltl_specs = [g.one_condition(), g.rules_followed_then_goal(), g.there_exists_a_path()]
            ctl_specs = [g.ctl_rule_cannot_lead_into_dead(), g.ctl_rule_can_be_followed()]
            f.write(to_smv_format(f_domain, ltl_rules, ltl_specs, ctl_specs))
        if check_file(directory + filename):
            print(s)


def model_check_sketches_():
    domain = Miconic()
    directory = "smvs/"
    filename = "miconic_2.smv"
    real_sketch = domain.sketch_2()
    generator = construct_feature_generator()

    # (syntactic_element_factory, config.complexity, config.time_limit, config.feature_limit, config.num_threads_feature_generator, dlplan_states)  # generate features with all states of instances
    feature_reprs = generator.generate(domain.factory(), 5, 5, 5, 5, 5, 180, 100000, 1, domain.dl_system().states)

    numerical_features = [domain.factory().parse_numerical(r, i) for i, r in enumerate(feature_reprs) if r.startswith("n_")]
    print(numerical_features)
    boolean_features = [domain.factory().parse_boolean(r, i) for i, r in enumerate(feature_reprs) if r.startswith("b_")]

    feature_sets = get_feature_sets(boolean_features, numerical_features, 1)

    transition_str = transition_system_to_smv(domain.dl_system())


    for bs, ns in tqdm(feature_sets):
        sketches = generate_sketches(bs, ns, 1)

        f_domain = domain.dl_system().add_features(bs + ns)
        for s in sketches:
            # print(s)
            tups = list_to_ruletups(s)
            # print("t", tups)
            arrow_sketch = ruletups_to_arrowsketch(tups)
            # print("as", arrow_sketch.show())
            # print(f_domain.get_feature_bounds())
            ltl_rules = fill_in_rules(arrow_sketch.rules, f_domain.get_feature_bounds())
            # print("ltl", ltl_rules)
            if len(ltl_rules) > 0:
                g = FormulaGenerator(len(ltl_rules))
                with open(directory + filename, 'w') as f:
                    ltl_specs = [g.one_condition(), g.rules_followed_then_goal(), g.there_exists_a_path()]
                    ctl_specs = [g.ctl_rule_cannot_lead_into_dead(), g.ctl_rule_can_be_followed()]
                    f.write(to_smv_format(f_domain, ltl_rules, ltl_specs, ctl_specs))
                if check_file(directory + filename):
                    print(arrow_sketch.show() + '\n')


def model_check_sketches_bis():
    domain = Gripper()
    directory = "smvs/"
    filename = "gripper.smv"
    generator = construct_feature_generator()

    # (syntactic_element_factory, config.complexity, config.time_limit, config.feature_limit, config.num_threads_feature_generator, dlplan_states)  # generate features with all states of instances
    feature_reprs = generator.generate(domain.factory(), 5, 5, 5, 5, 5, 180, 100000, 1, domain.dl_system.states)

    numerical_features = [domain.factory().parse_numerical(r, i) for i, r in enumerate(feature_reprs) if r.startswith("n_")]
    print(numerical_features)
    boolean_features = [domain.factory().parse_boolean(r, i) for i, r in enumerate(feature_reprs) if r.startswith("b_")]

    feature_sets = get_feature_sets(boolean_features, numerical_features, 1)
    print(f"numerical: {len(numerical_features)}")
    print(f"bools: {len(boolean_features)}")
    transition_str = transition_system_to_smv(domain.dl_system)
    # j = 0
    # for s in feature_sets:
    #    j = j+1
    # print(j)
    # print(comb(len(numerical_features) + len(boolean_features), 2))
    i = 0
    for bs, ns in tqdm(feature_sets):
        rules: Iterator[tuple[list[Condition], list[Effect]]] = generate_rules(bs, ns)
        def check_rule_file(filepath: str) -> bool:
            pynusmv.init.init_nusmv()
            pynusmv.glob.load_from_file(filepath=filepath)
            pynusmv.glob.compute_model()
            fsm = pynusmv.glob.prop_database().master.bddFsm
            ctls = [pynusmv.glob.prop_database()[0]]
            check = not pynusmv.mc.check_ctl_spec(fsm, ctls[0].expr)
            pynusmv.init.deinit_nusmv()
            return check

        def model_check_rule(f_domain, rule: tuple[list[Condition], list[Effect]], filepath: str = None) -> bool:
            tups = list_to_ruletups((rule,))
            arrow_rule = ruletups_to_arrowsketch(tups)
            ltl_rules = fill_in_rules(arrow_rule.rules, f_domain.get_feature_bounds())
            if len(ltl_rules) > 0:
                g = FormulaGenerator(len(ltl_rules))
                with open(filepath, 'w') as f:
                    ltl_specs = []
                    ctl_specs = [g.ctl_rule_cannot_lead_into_dead()]
                    f.write(to_smv_format(f_domain, ltl_rules, ltl_specs, ctl_specs))

            return check_rule_file(filepath)
        f_domain = domain.dl_system.add_features(bs + ns)
        filtered_rules = filter(lambda r: model_check_rule(f_domain, r, directory + "miconic_2_r.smv"), rules)
        #print(len(list(filtered_rules)))
        sketches = generate_sketches_from_rules(filtered_rules, 1)


        for s in sketches:
            i = i+1
            tups = list_to_ruletups(s)
            arrow_sketch = ruletups_to_arrowsketch(tups)
            if model_check_sketch(f_domain, arrow_sketch, directory + filename):
                yield arrow_sketch
            # print(i)


class Data:
    def __init__(self):
        # self._domain_file = "domain.pddl??"
        # self.domain = get_domain_problem(self.domain_file)
        # self._instance_files = ["instance.pddl??", ""]
        self.transition_systems = ["instance_system", "..."]
        self.features = "features???"


def make_data_files(directory: str):
    """

    :param directory: We assume that the directory has one domain file called "domain.pddl", and all the remaining files are instance files
    :return:
    """
    domain_path: str = directory + "/domain.pddl"
    domain = src.transition_system.tarski.load_domain(domain_path)
    instance_files: list[str] = sorted(os.listdir(directory))
    instance_files.remove("domain.pddl")
    print(instance_files)

    states_per_instance: dict[str, list[dlplan.State]] = {}

    for i_file in tqdm(instance_files):
        iproblem = ts.tarski.load_instance(domain_path, directory + '/' + i_file)
        instance = ts.conversions.dlinstance_from_tarski(domain, iproblem)
        tarski_system: ts.tarski.TarskiTransitionSystem = ts.tarski.from_instance(iproblem)
        dl_system: ts.dlplan.DLTransitionModel = ts.conversions.tarski_to_dl_system(tarski_system, instance)

        with open("transition_systems/" + directory + '/' + i_file.removesuffix(".pddl") + ".json", "w") as trans_file:
            json.dump({"init": dl_system.initial_state, "goal": dl_system.goal_states, "graph": dl_system.graph.adj}, trans_file)

        with open("data/state_files/" + directory + '/' + i_file.removesuffix(".pddl") + ".json", "w") as state_file:
            # json.dump([[(instance.get_atom(atom_idx).get_predicate().get_name(), [object.get_name() for object in instance.get_atom(atom_idx).get_objects()]) for atom_idx in state.get_atom_idxs()] for state in dl_system.states], state_file)
            json.dump([[instance.get_atom(atom_idx).get_name() for atom_idx in state.get_atom_idxs()] for state in dl_system.states], state_file)

        states_per_instance[i_file.removesuffix(".pddl")] = dl_system.states

    #vocab: dlplan.VocabularyInfo = src.transition_system.conversions.dlvocab_from_tarski(domain.language)
    vocab: dlplan.VocabularyInfo = list(states_per_instance.values())[0][0].get_instance_info().get_vocabulary_info()
    factory: dlplan.SyntacticElementFactory = dlplan.SyntacticElementFactory(vocab)

    generator = construct_feature_generator()
    feature_reprs = generator.generate(factory, 5, 5, 5, 5, 5, 180, 100000, 1, [s for sts in states_per_instance.values() for s in sts])
    numerical_features: list[dlplan.Numerical] = [factory.parse_numerical(r, i) for i, r in enumerate(feature_reprs) if r.startswith("n_")]
    boolean_features = [factory.parse_boolean(r, i) for i, r in enumerate(feature_reprs) if r.startswith("b_")]

    for file, sts in states_per_instance.items():
        with open("feature_valuations/" + file + ".json", "w") as feature_file:
            for f in numerical_features:
                for s in sts:
                    f.evaluate(s)
            json.dump({f.compute_repr(): [f.evaluate(s) for s in sts] for f in numerical_features + boolean_features}, feature_file)



def read_states(instance: dlplan.InstanceInfo, state_file: str) -> list[dlplan.State]:
    with open(state_file, "r") as sf:
        data = json.load(sf)
    return [dlplan.State(instance, [instance.get_atom(instance.get_atom_idx(str(a))) for a in state]) for state in data]


def test_read_states():
    domain_path: str = "gripper/domain.pddl"
    domain = src.transition_system.tarski.load_domain(domain_path)
    instance_path: str = "gripper_test/p-1-0.pddl"

    iproblem = ts.tarski.load_instance(domain_path, instance_path)
    instance = ts.conversions.dlinstance_from_tarski(domain, iproblem)

    states = read_states(instance, "data/state_files/gripper_test/p-1-0.json")
    for i, state in enumerate(states):
        print(i, [instance.get_atom(idx) for idx in state.get_atom_idxs()])








"""
def read_data() -> Data:
    pass


def model_check_from_files():
    domain = ???
    boolean_features = domain.get_boolean_features()
    numerical_features = ???
    feature_sets = get_feature_sets(boolean_features, numerical_features, 1)
    for bs, ns in tqdm(feature_sets):
        rules = generate_rules(bs, ns)
        filtered_rules = filter(lambda r: all([model_check.rule(i, r, directory + "miconic_2_r.smv") for i in domain.instances]), rules)
        sketch_pool = generate_sketches_from_rules(filtered_rules, 1)

        for s in sketch_pool:
            if all(model_check.sketch(i, s, directory) for i in domain.instances):
                yield s
"""


if __name__ == '__main__':
    #make_data_files("gripper_test")
    test_read_states()
