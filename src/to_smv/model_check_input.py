from src.transition_system.dl_transition_model import DLTransitionModel, DLFeatureTransitionModel
from src.dlplan_utils import repr_feature
from ltl import *
from src.logics.feature_vars import *


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


def ltl_to_smv(ltl) -> str:
    match ltl:
        case Top(): return "TRUE"
        case Bottom(): return "FALSE"
        case BooleanVar(f, v): return f"{repr_feature(f)}={str(v).upper()}"
        case NumericalVar(f, v): return f"{repr_feature(f)}={str(v).upper()}"
        case Var(s) as x:
            print(f"error: normal var {x} in ltl formula") # TODO exception handling
            return None
        case Not(p): return f"!{ltl_to_smv(p)}"
        case And(p, q): return f"({ltl_to_smv(p)} & {ltl_to_smv(q)})"
        case Or(p, q): return f"({ltl_to_smv(p)} | {ltl_to_smv(q)})"
        case Next(p): return f"X({ltl_to_smv(p)})"
        case Until(p, q): return f"({ltl_to_smv(p)} U {ltl_to_smv(q)})"
        case Release(p, q):  return f"({ltl_to_smv(p)} V {ltl_to_smv(q)})"
        case Then(p, q): return f"({ltl_to_smv(p)} -> {ltl_to_smv(q)})"
        case Iff(p, q): return f"({ltl_to_smv(p)} <-> {ltl_to_smv(q)})"
        case Finally(p): return f"F({ltl_to_smv(p)})"
        case Globally(p): return f"G({ltl_to_smv(p)})"
        case Weak(p, q):  # = Release(q, Or(p, q))
            return f"{ltl_to_smv(Release(q, p | q))}"
        case Strong(p, q):  # = Until(q, And(p, q))
            return f"({ltl_to_smv(Until(q, p & q))})"
        case _: raise NotImplementedError

