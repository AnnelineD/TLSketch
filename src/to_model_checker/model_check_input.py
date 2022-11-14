from src.transition_system.dl_transition_model import DLTransitionModel
from src.dlplan_utils import repr_feature


def convert_transition_system(transition_system: DLTransitionModel):
    nl = '\n'   # f-strings cannot include backslashes
    return f"MODULE main\nVAR " \
        f"  state: {{{', '.join([f's{s.id}' for s in transition_system.states])}}};" \
        f"ASSIGN" \
        f"  init(state) := {transition_system.init_state.id};" \
        f"  next(state) := case" \
        f"{nl.join(f'''          state = s{s.id}: {{{ ', '.join(f's{t.id}' for t in transition_system.targets[s]) }}}''' for s in transition_system.states)};" \
        f"                 esac"


def convert_features(ts: DLTransitionModel):
    tab = '\t'
    nl = '\n'
    return f"DEFINE \n " \
    f"{nl.join(f''' {tab}{repr_feature(fn)} := case {nl + tab + tab}{(nl + tab + tab).join(f'state = s{s.get_index()}: {ts.features[fn][s]};' for s in ts.states)}''' for fn in ts.features.keys())}" \
    f"\n \t esac;"


def convert_ltl_statement(ltl):
    pass
