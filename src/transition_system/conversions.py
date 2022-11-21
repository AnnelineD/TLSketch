import dlplan
from src.transition_system.tarski_transition_model import *
from src.transition_system.tarski_manipulation import sort_constants, typed_permutations
from src.transition_system.dl_transition_model import DLTransitionModel


def tarski_predicate_to_tuple(p: tarski.syntax.predicate.Predicate) -> tuple[str, int]:
    return p.name, len(p.sort)


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


def dlinstance_from_tarski(domain_lan: tarski.fol.FirstOrderLanguage, instance_lan: tarski.fol.FirstOrderLanguage) -> dlplan.InstanceInfo:
    v: dlplan.VocabularyInfo = dlvocab_from_tarski(domain_lan)
    i = dlplan.InstanceInfo(v)
    d: dict[TSort, list[TConstant]] = sort_constants(instance_lan)

    for p in domain_lan.predicates:
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
    return dlplan.State(i, [i.get_atom(i.get_atom_idx(str(a))) for a in state.as_atoms()])


def tmodels_to_dlstates(states: list[TModel], i: dlplan.InstanceInfo) -> list[dlplan.State]:
    return [tmodel_to_dlstate(tstate, i) for tstate in states]


def tarski_to_dl_system(ts: TarskiTransitionSystem, i) -> DLTransitionModel:
    states = tmodels_to_dlstates(ts.states, i)
    init = states[ts.states.index(ts.instance.init)]
    return DLTransitionModel(i, states, init, ts.graph)


"""
def add_feature_props(system: TarskiTransitionSystem, feature):
    if isinstance(feature, dlplan.Boolean):
        model.b_features.append(feature)
    if isinstance(feature, dlplan.Numerical):
        model.n_features.append(feature)
"""