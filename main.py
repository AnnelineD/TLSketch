from functools import reduce

import dlplan
import ltl
import pynusmv
from examples import *
from src.logics.rules import LTLSketch
from src.sketch_generation.generation import generate_sketches
from src.to_smv.conversion import *
from src.logics.sketch_to_ltl import policy_to_arrowsketch, fill_in_rule, fill_in_rules, list_to_ruletups, \
    ruletups_to_arrowsketch
from src.logics.formula_generation import FormulaGenerator


def show_domain_info():
    domain = Miconic()
    print(domain.dl_system().graph.show())
    print(domain.dl_system().graph.adj)

    sketch = domain.sketch_2()
    print("sketch", sketch)
    print()
    f_domain = domain.dl_system().add_features(sketch.get_boolean_features() + sketch.get_numerical_features())
    arrow_sketch = policy_to_arrowsketch(sketch)
    print("features: ", f_domain.features.keys())
    print("arrow sketch:", arrow_sketch.show())

    print("bounds:", f_domain.get_feature_bounds())
    ltl_rules = fill_in_rules(arrow_sketch.rules, f_domain.get_feature_bounds())
    goal_atoms = domain.dl_system().instance_info.get_static_atoms()
    print("goal atoms", goal_atoms)
    for i, s in enumerate(domain.dl_system().states):
        print(i, s)
    print()
    print("smv:")
    print("MODULE main")
    print(transition_system_to_smv(domain.dl_system()))
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
    f_domain = domain.dl_system().add_features(sketch.get_boolean_features() + sketch.get_numerical_features())
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
    for s in sketches:
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
            f.write("MODULE main\n")
            f.write(transition_system_to_smv(domain.dl_system()) + '\n')
            f.write(features_to_smv(f_domain) + '\n')
            f.write(rules_to_smv(ltl_rules) + '\n')
            f.write("LTLSPEC " + ltl_to_smv(g.one_condition()) + ";" + '\n')
            f.write("LTLSPEC " + ltl_to_smv(g.rules_followed_then_goal()) + ";" + '\n')
            f.write("LTLSPEC " + ltl_to_smv(g.there_exists_a_path()) + ";" + '\n')
        pynusmv.init.init_nusmv()
        pynusmv.glob.load_from_file(directory + filename)
        pynusmv.glob.compute_model()
        evals = [pynusmv.mc.check_ltl_spec(p.expr) for p in pynusmv.glob.prop_database()]
        if evals == [True, True, False]:
            print(s)
        pynusmv.init.deinit_nusmv()


if __name__ == '__main__':
    model_check_sketches()
