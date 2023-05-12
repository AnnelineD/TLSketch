import dlplan
import tarski.fstrips

#from .tarski import TarskiTransitionSystem
from .tarski_manipulation import sort_constants, typed_permutations
from .dlplan import DLTransitionModel
from .types import *
from .transition_system import StateStr

"""
def tarski_predicate_to_tuple(p: tarski.syntax.predicate.Predicate) -> tuple[str, int]:
    return p.name, len(p.sort)
"""


def dlvocab_from_tarski(domain_lan: tarski.fol.FirstOrderLanguage, add_goals=True) -> dlplan.VocabularyInfo:
    v = dlplan.VocabularyInfo()
    for p in domain_lan.predicates:
        if isinstance(p.name, str):
            v.add_predicate(str(p.name), p.arity)
            if add_goals:
                v.add_predicate(str(p.name) + '_g', p.arity)
    for c in domain_lan.constants():
        v.add_constant(c.name)
    return v


def dlinstance_from_tarski(domain: tarski.fstrips.Problem, instance: tarski.fstrips.Problem) -> dlplan.InstanceInfo:
    v: dlplan.VocabularyInfo = dlvocab_from_tarski(domain.language)
    i = dlplan.InstanceInfo(v)
    d: dict[TSort, list[TConstant]] = sort_constants(instance.language)
    goal = instance.goal

    for p in domain.language.predicates:
        if isinstance(p.name, str):
            if not p.sort:
                i.add_atom(p.name, [])
            else:
            # TODO delete the on(b1, b1)
                combs: list[tuple[TConstant]] = typed_permutations(p.sort, d)
                for c in combs:
                    i.add_atom(p.name, [obj.name for obj in c])

    def add_goal(g):
        match g:
            case tarski.syntax.Atom(): i.add_static_atom(g.predicate.name + '_g', [a.name for a in g.subterms])
            case tarski.syntax.CompoundFormula():
                match g.connective:
                    case tarski.syntax.Connective.And:
                        for s in g.subformulas: add_goal(s)
                    case _:
                        raise NotImplementedError(g.connective)
            case _: raise NotImplementedError

    add_goal(goal)
    return i

"""
def tmodel_to_dlstate(tstate: TModel, i: dlplan.InstanceInfo) -> dlplan.State:
    "function rewrites tarski states to dlplan states"
    return dlplan.State(i, [i.get_atom(i.get_atom_idx(str(a))) for a in tstate.as_atoms()])
"""
"""
def tmodels_to_dlstates(states: list[TModel], i: dlplan.InstanceInfo) -> list[dlplan.State]:
    return [tmodel_to_dlstate(tstate, i) for tstate in states]
"""



"""
def tarski_to_dl_system(ts: TarskiTransitionSystem, i) -> DLTransitionModel:
    states = [tmodel_to_dlstate(tstate, i) for tstate in ts.states]
    return DLTransitionModel(i, states, ts.states.index(ts.init), ts.goal_states, ts.graph)
"""

"""
def add_feature_props(system: TarskiTransitionSystem, feature):
    if isinstance(feature, dlplan.Boolean):
        model.b_features.append(feature)
    if isinstance(feature, dlplan.Numerical):
        model.n_features.append(feature)
"""