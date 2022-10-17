import dlplan
from tarski.io import PDDLReader

from src.tarski_transition_model import *
from src.dl_transition_model import *
from src.conversions import *


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

    print(feature_sys.states)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
