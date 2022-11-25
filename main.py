from functools import reduce

import dlplan
import ltl

from examples import *
from src.logics.rules import LTLSketch
from src.to_smv.conversion import *
from src.logics.sketch_to_ltl import policy_to_arrowsketch, fill_in_rule, fill_in_rules


def main():
    domain = BlocksClear()

    sketch = domain.sketch_1()
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
    print(ltl_to_smv(ltl_sketch.get_formula()))


if __name__ == '__main__':
    main()
