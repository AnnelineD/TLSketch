import dlplan

from examples import *
from src.logics.rules import LTLSketch
from src.to_smv.conversion import *
from src.logics.sketch_to_ltl import policy_to_arrowsketch, fill_in_rule, fill_in_rules


def main():
    domain = BlocksOn()
    #print("MODULE main")
    #print(transition_system_to_smv(domain.dl_system()))

    sketch = domain.sketch_0()
    f1 = sketch.get_boolean_features()[0]
    print(f1, f1.get_index())
    print("sketch", sketch)
    print("rule", sketch.get_rules()[0])
    print()
    f_domain = domain.dl_system().add_features(sketch.get_boolean_features() + sketch.get_numerical_features())
    # print(features_to_smv(f_domain))
    arrow_sketch = policy_to_arrowsketch(sketch)
    print("features: ", f_domain.features.keys())
    print("arrow:", arrow_sketch.show())
    print("arrow2: ", arrow_sketch.rules)
    print(f_domain.get_feature_bounds())
    ltl_rules = fill_in_rules(arrow_sketch.rules, f_domain.get_feature_bounds())
    ltl_sketch = LTLSketch(ltl_rules)

    print(ltl_sketch.show())


if __name__ == '__main__':
    main()
