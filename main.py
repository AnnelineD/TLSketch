from src.transition_system.dl_transition_model import *
from src.transition_system.conversions import *
from dlplan import PolicyReader
from src.logics.sketch_to_ltl import *


def pddl_to_dlplan_states(domain_file: str, instance_file: str):
    reader = PDDLReader(raise_on_error=True)
    tproblem: TProblem = reader.read_problem(domain_file, instance_file)
    tsystem = TarskiTransitionSystem(tproblem)

    i = dlinstance_from_tarski(tproblem.language)
    dlstates = tmodels_to_dlstates(tsystem.states, i)
    dlsystem = DLTransitionModel(i, dlstates)
    return dlsystem


if __name__ == '__main__':
    dlsystem = pddl_to_dlplan_states("blocks_4_clear/domain.pddl", "blocks_4_clear/p-3-0.pddl")
    factory = dlplan.SyntacticElementFactory(dlsystem.instance_info.get_vocabulary_info())
    n = factory.parse_numerical("n_count(c_primitive(on,0))")
    H = factory.parse_boolean("b_nullary(arm-empty)")
    feature_sys = add_features(dlsystem, {n, H})

    # print(feature_sys.states)

    sketch: dlplan.Policy = PolicyReader().read('(:policy'
                                                '\n(:boolean_features "b_nullary(arm-empty)")'
                                                '\n(:numerical_features "n_count(c_primitive(on,0))")'
                                                '\n(:rule (:conditions (:c_n_gt 0)) (:effects (:e_b_pos 0) (:e_n_bot 0)))'
                                                '\n(:rule (:conditions (:c_n_gt 0)) (:effects (:e_b_neg 0) (:e_n_dec 0)))'
                                                '\n)', factory)

    r: dlplan.Rule = sketch.get_rules()[0]
    r2 = sketch.get_rules()[1]
    c: dlplan.BaseCondition = r.get_conditions()[0]
    #print(c.get_base_feature())
    #print("here", type(r.get_conditions()))
    from src.dlplan_utils import show_sketch
    #print(show_condition(c, "c"))

    print(show_sketch(sketch))

    num_ltl = to_num_ltl(sketch)
    for r in num_ltl.full_rules:
        print(r.show())

    # print(policy_to_rule_tuples(sketch))


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
