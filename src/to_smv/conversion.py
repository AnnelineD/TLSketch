from src.logics.rules import LTLSketch, ExpandedSketch
#from src.transition_system.dlplan import DLTransitionModel, DLFeatureTransitionModel
from src.dlplan_utils import repr_feature
from ltl import *
from src.logics.feature_vars import *
from src.transition_system.graph import DirectedGraph
import ctl


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

"""
def transition_system_to_smv(transition_system: DLTransitionModel):
    return graph_to_smv(transition_system.graph, transition_system.initial_state)


def features_to_smv(ts: DLFeatureTransitionModel):
    tab = '\t'
    nl = '\n'
    return f"DEFINE \n " \
    f"{nl.join(f''' {tab}{repr_feature(fn)} := case {nl + tab + tab}{(nl + tab + tab).join(f'state = s{s.get_index()}: {str(ts.features[fn][s]).upper()};' for s in ts.transition_model.states)} {nl + tab}esac;''' for fn in ts.features.keys())}\n"\
    f"{tab}goal := state in {{{', '.join({f's{i}' for i in ts.transition_model.goal_states})}}};"
"""

def valuations_to_smv(vals: dict[str, list[Union[bool, int]]], goals: list[int], features: set[str]) -> str:
    tab = '\t'
    nl = '\n'
    return f"DEFINE \n " \
           f"{nl.join(f''' {tab}{repr_feature_str(fn)} := case {nl + tab + tab}{(nl + tab + tab).join(f'state = s{e}: {str(s).upper()};' for e, s in enumerate(vals[fn]))} {nl + tab}esac;''' for fn in features)}\n" \
           f"{tab}goal := state in {{{', '.join(f's{i}' for i in goals)}}};"

"""
def rules_to_smv(rules: list[LTLRule]) -> str:
    return '\n'.join([f"\tc{i} := {ltl_to_smv(r.conditions)}; \n \te{i} := {ltl_to_smv(r.effects)};" for i, r in enumerate(rules)])
"""


def rules_to_smv(exp_sketch: ExpandedSketch) -> str:
    return '\n'.join([f"\tc{i} := {' & '.join(repr_feature_vars(c) for c in r.conditions)}; \n "
                      f"\te{i} := {' & '.join(repr_feature_vars(e) for e in r.effects)};"
                      for i, r in enumerate(exp_sketch.rules)])


def repr_feature_vars(fv: FeatureVar):
    match fv:
        case BooleanVar(f, True, o):
            return repr_feature_str(f)
        case BooleanVar(f, False, o):
            return f"!{repr_feature_str(f)}"
        case NumericalVar(f, v, o):
            return f"{repr_feature_str(f)}{o}{v}"

def ltl_to_smv(ltl: LTLFormula) -> str:
    match ltl:
        case Top(): return "TRUE"
        case Bottom(): return "FALSE"
        case BooleanVar(f, v): return f"{repr_feature_str(f)}={str(v).upper()}"
        case NumericalVar(f, v): return f"{repr_feature_str(f)}={str(v).upper()}"
        case Var(s) as x: return f"{s}"  # TODO make a special goal var
        case Not(p): return f"!{ltl_to_smv(p)}"
        case And(p, q): return f"({ltl_to_smv(p)} & {ltl_to_smv(q)})"
        case Or(p, q): return f"({ltl_to_smv(p)} | {ltl_to_smv(q)})"
        case Next(p): return f"X({ltl_to_smv(p)})"
        case Until(p, q): return f"({ltl_to_smv(p)} U {ltl_to_smv(q)})"
        case Release(p, q): return f"({ltl_to_smv(p)} V {ltl_to_smv(q)})"
        case Then(p, q): return f"({ltl_to_smv(p)} -> {ltl_to_smv(q)})"
        case Iff(p, q): return f"({ltl_to_smv(p)} <-> {ltl_to_smv(q)})"
        case Finally(p, bound):
            if not bound: return f"F({ltl_to_smv(p)})"
            else:
                s, e = bound
                return f"F[{s}, {e}]({ltl_to_smv(p)})"
        case Globally(p): return f"G({ltl_to_smv(p)})"
        case Weak(p, q):  # = Release(q, Or(p, q))
            return f"{ltl_to_smv(Release(q, p | q))}"
        case Strong(p, q):  # = Until(q, And(p, q))
            return f"({ltl_to_smv(Until(q, p & q))})"
        case Previous(p):
            return f"Y({ltl_to_smv(p)})"
        case Once(p, bound):
            if not bound: return f"O({ltl_to_smv(p)})"
            else:
                s, e = bound
                return f"O[{s}, {e}]({ltl_to_smv(p)})"

        case _: raise NotImplementedError(ltl)


def ctl_to_smv(f: ctl.CTLFormula) -> str:
    match f:
        case ctl.Top(): return "TRUE"
        case ctl.Bottom(): return "FALSE"
        case ctl.Var(s) as x: return f"{s}"  # TODO make a special goal var
        case ctl.Not(p): return f"!{ctl_to_smv(p)}"
        case ctl.And(p, q): return f"({ctl_to_smv(p)} & {ctl_to_smv(q)})"
        case ctl.Or(p, q): return f"({ctl_to_smv(p)} | {ctl_to_smv(q)})"
        case ctl.EX(p): return f"EX({ctl_to_smv(p)})"
        case ctl.AX(p): return f"AX({ctl_to_smv(p)})"
        case ctl.Then(p, q): return f"({ctl_to_smv(p)} -> {ctl_to_smv(q)})"
        case ctl.Iff(p, q): return f"({ctl_to_smv(p)} <-> {ctl_to_smv(q)})"
        case ctl.EF(p, bound):
            if not bound: return f"EF({ctl_to_smv(p)})"
            else: NotImplementedError(f)
        case ctl.AF(p, bound):
            if not bound: return f"AF({ctl_to_smv(p)})"
            else: NotImplementedError(f)
        case ctl.EG(p): return f"EG({ctl_to_smv(p)})"
        case ctl.AG(p): return f"AG({ctl_to_smv(p)})"
        case _: raise NotImplementedError(f)


#TODO find good representations
def repr_feature_str(feature: str):
    return feature.replace("(", "").replace(")", "").replace(',', '').replace("-", "")
