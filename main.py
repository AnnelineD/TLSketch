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
import src.file_manager as fm


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


def write_all_transition_systems(directory: str):
    domain_path: str = directory + "/domain.pddl"
    domain = src.transition_system.tarski.load_domain(domain_path)
    instance_files: list[str] = sorted(os.listdir(directory))
    instance_files.remove("domain.pddl")

    for i_file in tqdm(instance_files):
        iproblem = ts.tarski.load_instance(domain_path, directory + '/' + i_file)
        instance = ts.conversions.dlinstance_from_tarski(domain, iproblem)
        tarski_system: ts.tarski.TarskiTransitionSystem = ts.tarski.from_instance(iproblem)
        dl_system: ts.dlplan.DLTransitionModel = ts.conversions.tarski_to_dl_system(tarski_system, instance)

        fm.write.transition_system(dl_system.graph, dl_system.initial_state, dl_system.goal_states, f"data/{directory}/transition_systems/{i_file.removesuffix('.pddl')}.json")
        fm.write.dl_states(dl_system.states, f"data/{directory}/states/{i_file.removesuffix('.pddl')}.json")

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
            json.dump({f.compute_repr(): [f.evaluate(s) for s in sts] for f in numerical_features + boolean_features}, feature_file)


def write_all_instances(directory: str, instance_files: list[str], domain_file: str, ts_dir, states_dir):
    domain = ts.tarski.load_domain(directory + '/' + domain_file)
    for i_file in tqdm(instance_files):
        iproblem = ts.tarski.load_instance(directory + '/' + domain_file, directory + '/' + i_file)
        instance = ts.conversions.dlinstance_from_tarski(domain, iproblem)
        tarski_system: ts.tarski.TarskiTransitionSystem = ts.tarski.from_instance(iproblem)
        dl_system: ts.dlplan.DLTransitionModel = ts.conversions.tarski_to_dl_system(tarski_system, instance)

        fm.write.transition_system(dl_system.graph, dl_system.initial_state, dl_system.goal_states, ts_dir + '/' + i_file.removesuffix(".pddl") + ".json")
        fm.write.dl_states(dl_system.states, states_dir + '/' + i_file.removesuffix(".pddl") + ".json")


def make_feature_file(states: list[dlplan.State], file_path: str, factory: dlplan.SyntacticElementFactory):
    generator = construct_feature_generator()
    feature_reprs = generator.generate(factory, 5, 5, 5, 5, 5, 180, 100000, 1, states)
    with open(file_path, 'w') as fp:
        json.dump(feature_reprs, fp)
    return feature_reprs


def parse_features(feature_reprs: list[str], factory: dlplan.SyntacticElementFactory) -> tuple[list[dlplan.Boolean], list[dlplan.Numerical]]:
    boolean_features: list[dlplan.Boolean] = [factory.parse_boolean(r, i) for i, r in enumerate(feature_reprs) if r.startswith("b_")]
    numerical_features: list[dlplan.Numerical] = [factory.parse_numerical(r, i) for i, r in enumerate(feature_reprs) if r.startswith("n_")]
    return boolean_features, numerical_features


def write_feature_valuations(states: list[dlplan.State], features: list[any], file_path: str):
    with open(file_path, "w") as feature_file:
        json.dump({f.compute_repr(): [f.evaluate(s) for s in states] for f in features}, feature_file)


def read_feature_reprs(file_path) -> list[str]:
    with open(file_path) as fp:
        return json.load(fp)


def test_read_states():
    domain_path: str = "gripper/domain.pddl"
    domain = src.transition_system.tarski.load_domain(domain_path)
    instance_path: str = "gripper_test/p-1-0.pddl"

    iproblem = ts.tarski.load_instance(domain_path, instance_path)
    instance = ts.conversions.dlinstance_from_tarski(domain, iproblem)

    states = fm.read.dl_states("data/state_files/gripper_test/p-1-0.json", instance)
    for i, state in enumerate(states):
        print(i, [instance.get_atom(idx) for idx in state.get_atom_idxs()])


def read_valuations(file_path) -> dict[str, list[Union[bool, int]]]:
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


class Instance:
    def __init__(self, transitions_sys: DirectedGraph, init: int, goal_states: list[int], valuations: dict[str, list[Union[bool, int]]]):
        assert(init <= transitions_sys.size())
        assert(all([g <= transitions_sys.size() for g in goal_states]))
        assert(all([len(valuations[k]) == transitions_sys.size() for k in valuations.keys()]))
        self.system = transitions_sys
        self.init = init
        self.goal_states = goal_states
        self.valuations = valuations


def read_instance(transition_path, valuation_path) -> Instance:
        graph, init, goal = fm.read.transition_system(transition_path)
        valuations = read_valuations(valuation_path)
        return Instance(graph, init, goal, valuations)


def graph_to_smv(graph: DirectedGraph, init_index):
    assert init_index < graph.size()
    nl = '\n'   # f-strings cannot include backslashes
    return f"VAR \n" \
           f"  state: {{{', '.join([f's{i}' for i in range(graph.size())])}}};\n" \
           f"ASSIGN \n" \
           f"  init(state) := s{init_index}; \n" \
           f"  next(state) := case \n" \
           f"{nl.join(f'''          state = s{i}: {{{ ', '.join(f's{t}' for t in graph.nbs(i)) }}};''' for i in range(graph.size()))}\n" \
           f"                 esac;"

def features_to_smv(features: list[Union[dlplan.Boolean, dlplan.Numerical]], instance: Instance):
    tab = '\t'
    nl = '\n'
    return f"DEFINE \n " \
           f"{nl.join(f''' {tab}{repr_feature(fn)} := case {nl + tab + tab}{(nl + tab + tab).join(f'state = s{s_idx}: {str(val).upper()};' for s_idx, val in enumerate(instance.valuations[fn.compute_repr()]))} {nl + tab}esac;''' for fn in features)}\n" \
           f"{tab}goal := state in {{{', '.join({f's{i}' for i in instance.goal_states})}}};"

def make_instance_smv(i: Instance, features):
    return "MODULE main\n" \
           + graph_to_smv(i.system, i.init) + '\n' \
           + features_to_smv(features, i) + '\n'

def get_instance_names(directory):
    instance_files: list[str] = sorted(os.listdir(directory))
    instance_files.remove("domain.pddl")
    return [fn.removesuffix(".pddl") for fn in instance_files]


def make_instance_smvs(directory, features):
    instances = get_instance_names(directory)
    for instance_name in instances:
        i = read_instance(f"data/{directory}/transition_systems/{instance_name}.json", f"data/{directory}/feature_valuations/{instance_name}.json")
        smv_format = make_instance_smv(i, features)
        with open(f"data/{directory}/smvs/{instance_name}.smv", "w") as f:
            f.write(smv_format)


def ltl_to_input(f: ltl.LTLFormula) -> pynusmv.prop.Spec:
    from pynusmv import prop
    match f:
        case Top(): return prop.true()
        case Bottom(): return prop.false()
        case BooleanVar(f, v): return prop.atom(f"{repr_feature(f)}={str(v).upper()}")
        case NumericalVar(f, v): return prop.atom(f"{repr_feature(f)}={str(v).upper()}")
        case Var(s) as x: return prop.atom(f"{s}")  # TODO make a special goal var
        case Not(p): return prop.not_(ltl_to_input(p))
        case And(p, q): return ltl_to_input(p) & ltl_to_input(q)
        case Or(p, q): return ltl_to_input(p) | ltl_to_input(q)
        case Next(p): return prop.x(ltl_to_input(p))
        case Until(p, q): return prop.u(ltl_to_input(p), ltl_to_input(q))
        case Release(p, q): raise NotImplementedError(Release(p, q))
        case Then(p, q): return prop.imply(ltl_to_input(p), ltl_to_input(q))
        case Iff(p, q): return prop.iff(ltl_to_input(p), ltl_to_input(q))
        case Finally(p, bound):
            if not bound: return prop.f(ltl_to_input(p))
            else:
                s, e = bound
                raise NotImplementedError("bound")
        case Globally(p): return prop.g(ltl_to_input(p))
        case Weak(p, q):  # = Release(q, Or(p, q))
            raise NotImplementedError("weak")
        case Strong(p, q):  # = Until(q, And(p, q))
            raise NotImplementedError("strong")
        case Previous(p):
            spec = ltl_to_input(p)
            s = prop.Spec(pynusmv.node.nsnode.find_node(pynusmv.parser.nsparser.OP_PREC, spec._ptr, None), freeit=False)
            s._car = spec
            return s
        case Once(p, bound):
            if not bound:
                spec = ltl_to_input(p)
                s = prop.Spec(pynusmv.node.nsnode.find_node(pynusmv.parser.nsparser.OP_ONCE, spec._ptr, None), freeit=False)
                s._car = spec
                return s
            else:
                s, e = bound
                raise NotImplementedError("strong")

        case _: raise NotImplementedError(ltl)


def ctl_to_input(f: ctl.CTLFormula) -> pynusmv.prop.Spec:
    from pynusmv import prop
    match f:
        case ctl.Top(): return prop.true()
        case ctl.Bottom(): return prop.false()
        case ctl.Var(s) as x: return prop.atom(f"{s}")  # TODO make a special goal var
        case ctl.Not(p): return prop.not_(ctl_to_input(p))
        case ctl.And(p, q): return ctl_to_input(p) & ctl_to_input(q)
        case ctl.Or(p, q): return ctl_to_input(p) | ctl_to_input(q)
        case ctl.EX(p): return prop.ex(ctl_to_input(p))
        case ctl.AX(p): return prop.ax(ctl_to_input(p))
        case ctl.Then(p, q): return prop.imply(ctl_to_input(p), ctl_to_input(q))
        case ctl.Iff(p, q): return prop.iff(ctl_to_input(p), ctl_to_input(q))
        case ctl.EF(p, bound):
            if not bound: return prop.ef(ctl_to_input(p))
            else: NotImplementedError(f)
        case ctl.AF(p, bound):
            if not bound: return prop.af(ctl_to_input(p))
            else: NotImplementedError(f)
        case ctl.EG(p): return prop.eg(ctl_to_input(p))
        case ctl.AG(p): return prop.ag(ctl_to_input(p))
        case _: raise NotImplementedError(f)


def model_check_from_files(directory):
    domain_file = f"{directory}/domain.pddl"
    instance_names = get_instance_names(directory)
    feature_file = f"data/{directory}/features.json"

    def transition_path(instance_name):
        return f"data/{directory}/transition_systems/{instance_name}.json"
    def feature_valuation_path(instance_name):
        return f"data/{directory}/feature_valuations/{instance_name}.json"
    def smv_path(instance_name):
            return f"data/{directory}/smvs/{instance_name}.smv"

    domain = ts.tarski.load_domain(domain_file)
    vocab: dlplan.VocabularyInfo = src.transition_system.conversions.dlvocab_from_tarski(domain.language)
    factory: dlplan.SyntacticElementFactory = dlplan.SyntacticElementFactory(vocab)

    boolean_features, numerical_features = parse_features(read_feature_reprs(feature_file), factory)
    feature_sets = get_feature_sets(boolean_features, numerical_features, 1)

    make_instance_smvs(directory, boolean_features + numerical_features)

    for bs, ns in tqdm(feature_sets):
        rules = generate_rules(bs, ns)
        #filtered_rules = filter(lambda r: all([model_check.rule(i, r, directory + "miconic_2_r.smv") for i in domain.instances]), rules)
        #sketch_pool = generate_sketches_from_rules(filtered_rules, 1)
        sketch_pool = generate_sketches_from_rules(rules, 1)
        """
        for s in sketch_pool:
            if all(model_check.sketch(i, s, directory) for i in domain.instances):
                yield s
        """
        for s in sketch_pool:
            tups = list_to_ruletups(s)
            # print("t", tups)
            arrow_sketch = ruletups_to_arrowsketch(tups)
            # print("as", arrow_sketch.show())
            checked = True
            for inst in instance_names:
                feature_vals:  dict[str, list[Union[bool, int]]] = read_valuations(feature_valuation_path(inst))
                bounds: dict[dlplan.Numerical, int] = {n: max(feature_vals[n.compute_repr()]) for n in numerical_features}
                ltl_rules: list[LTLRule] = fill_in_rules(arrow_sketch.rules, bounds)
                if len(ltl_rules) == 0:
                    checked = False
                    break

                if len(ltl_rules) > 0:
                    g = FormulaGenerator(len(ltl_rules))
                    ltl_specs = [g.one_condition(), g.rules_followed_then_goal(), g.there_exists_a_path()]
                    ctl_specs = [g.ctl_rule_cannot_lead_into_dead(), g.ctl_rule_can_be_followed()]

                    with open(smv_path(inst), 'r') as f:
                        system = f.read()

                    with open(f"data/{directory}/smvs/temp.smv", 'w') as f:
                        f.write(system + '\n' + rules_to_smv(ltl_rules) + '\n')

                    pynusmv.init.init_nusmv()
                    pynusmv.glob.load_from_file(filepath=f"data/{directory}/smvs/temp.smv")
                    pynusmv.glob.compute_model()
                    fsm = pynusmv.glob.prop_database().master.bddFsm

                    #map(lambda spec: pynusmv.mc.check_ctl_spec(ctl_to_input(spec)), ctl_specs)
                    if list(map(lambda spec: pynusmv.mc.check_ctl_spec(fsm, ctl_to_input(spec)), ctl_specs)) != [False, True]:
                        assert(checked)
                        checked = False
                        pynusmv.init.deinit_nusmv()
                        break
                    if list(map(lambda spec: pynusmv.mc.check_ltl_spec(ltl_to_input(spec)), ltl_specs)) != [True, True, False]:
                        assert(checked)
                        checked = False
                        pynusmv.init.deinit_nusmv()
                        break
                    pynusmv.init.deinit_nusmv()

            if checked:
                yield arrow_sketch

def main_write_everything():
    directory = "gripper_test"
    write_all_transition_systems("gripper_test")
    all_states = []
    instances = []

    for i in get_instance_names(directory):
        domain_path: str = f"{directory}/domain.pddl"
        domain = src.transition_system.tarski.load_domain(domain_path)
        instance_path: str = f"{directory}/{i}.pddl"

        iproblem = ts.tarski.load_instance(domain_path, instance_path)
        instance = ts.conversions.dlinstance_from_tarski(domain, iproblem)
        states = fm.read.dl_states(f"data/{directory}/states/{i}.json", instance)
        instances.append(instance)
        all_states.append(states)


    vocab: dlplan.VocabularyInfo = all_states[0][0].get_instance_info().get_vocabulary_info()
    factory: dlplan.SyntacticElementFactory = dlplan.SyntacticElementFactory(vocab)
    make_feature_file([s for sts in all_states for s in sts], f"data/{directory}/features.json", factory)
    boolean_features, numerical_features = parse_features(read_feature_reprs(f"data/{directory}/features.json"), factory)
    print(len(boolean_features), len(numerical_features))
    for e, i in enumerate(get_instance_names(directory)):
        write_feature_valuations(all_states[e], boolean_features + numerical_features, f"data/{directory}/feature_valuations/{i}.json")

    make_instance_smvs(directory, boolean_features + numerical_features)


if __name__ == '__main__':
    sketches = list(model_check_from_files("gripper_test"))
    for s in sketches:
        print(s.show())

    print()

    sketches_ = list(model_check_sketches_bis())
    for s in sketches_:
        print(s.show())

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

