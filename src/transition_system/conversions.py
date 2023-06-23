import dlplan
import tarski.fstrips

#from .tarski import TarskiTransitionSystem
from .tarski_manipulation import sort_constants, typed_permutations
from .types import *
from .transition_system import StateStr


def dlvocab_from_tarski(domain_lan: tarski.fol.FirstOrderLanguage, add_goals=True) -> dlplan.core.VocabularyInfo:
    v = dlplan.core.VocabularyInfo()
    for p in domain_lan.predicates:
        if isinstance(p.name, str):
            v.add_predicate(str(p.name), p.arity, False)
            if add_goals:
                v.add_predicate(str(p.name) + '_g', p.arity, True)
    for c in domain_lan.constants():
        v.add_constant(c.name)
    return v


def dlinstance_from_tarski(domain: tarski.fstrips.Problem, instance: tarski.fstrips.Problem) -> dlplan.core.InstanceInfo:
    v: dlplan.core.VocabularyInfo = dlvocab_from_tarski(domain.language)
    i = dlplan.core.InstanceInfo(v)
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
