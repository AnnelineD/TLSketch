import tarski
import dlplan
from src.tarski_transition_model import *
from src.tarski_manipulation import sort_constants, typed_permutations


def tarski_predicate_to_tuple(p: tarski.syntax.predicate.Predicate) -> tuple[str, int]:
    return p.name, len(p.sort)


def dlvocab_from_tarski(lan: tarski.fol.FirstOrderLanguage) -> dlplan.VocabularyInfo:
    # TODO if there are constants
    v = dlplan.VocabularyInfo()
    for p in lan.predicates:
        if isinstance(p.name, str):
            v.add_predicate(*tarski_predicate_to_tuple(p))
    return v


def dlinstance_from_tarski(lan: tarski.fol.FirstOrderLanguage) -> dlplan.InstanceInfo:
    v: dlplan.VocabularyInfo = dlvocab_from_tarski(lan)
    i = dlplan.InstanceInfo(v)
    d: dict[TSort, list[TConstant]] = sort_constants(lan)

    for p in lan.predicates:
        if isinstance(p.name, str):
            if not p.sort:
                i.add_atom(p.name, [])
            else:
            # TODO delete the on(b1, b1)
                combs: list[tuple[TConstant]] = typed_permutations(p.sort, d)
                for c in combs:
                    i.add_atom(p.name, [obj.name for obj in c])
    return i


def tmodel_to_dlstate(state: TModel, i: dlplan.InstanceInfo) -> dlplan.State:
    """function rewrites tarski states to dlplan states"""
    return dlplan.State(i, [i.get_atom(i.get_atom_idx(a.__str__())) for a in state.as_atoms()])


def tmodels_to_dlstates(states: set[TModel], i: dlplan.InstanceInfo) -> set[dlplan.State]:
    return set([tmodel_to_dlstate(tstate, i) for tstate in states])



"""
def add_feature_props(system: TarskiTransitionSystem, feature):
    if isinstance(feature, dlplan.Boolean):
        model.b_features.append(feature)
    if isinstance(feature, dlplan.Numerical):
        model.n_features.append(feature)
"""