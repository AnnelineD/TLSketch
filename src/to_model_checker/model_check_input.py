from src.transition_system.dl_transition_model import DLTransitionModel, DLFeatureTransitionModel
from src.dlplan_utils import repr_feature


def convert_transition_system(transition_system: DLTransitionModel):
    nl = '\n'   # f-strings cannot include backslashes
    return f"VAR \n" \
        f"  state: {{{', '.join([f's{i}' for i, s in enumerate(transition_system.states)])}}};\n" \
        f"ASSIGN \n" \
        f"  init(state) := s{transition_system.initial_state.get_index()}; \n" \
        f"  next(state) := case \n" \
        f"{nl.join(f'''          state = s{i}: {{{ ', '.join(f's{t}' for t in transition_system.graph.nbs(i)) }}};''' for i, s in enumerate(transition_system.states))}\n" \
        f"                 esac;"


def convert_features(ts: DLFeatureTransitionModel):
    tab = '\t'
    nl = '\n'
    return f"DEFINE \n " \
    f"{nl.join(f''' {tab}{repr_feature(fn)} := case {nl + tab + tab}{(nl + tab + tab).join(f'state = s{s.get_index()}: {str(ts.features[fn][s]).upper()};' for s in ts.transition_model.states)} {nl + tab}esac;''' for fn in ts.features.keys())}"

def convert_ltl_statement(ltl):
    pass
