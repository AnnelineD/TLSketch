# Functionality to translate domains and instances represented in classes Tarski library into classes from the dlplan
# library

import dlplan
import tarski.fstrips

from .tarski_manipulation import sort_constants, typed_permutations
from .types import *


def dlvocab_from_tarski(domain_lan: tarski.fol.FirstOrderLanguage, add_goals=True) -> dlplan.core.VocabularyInfo:
    """
    Given domain language from the tarski library, construct vocabulary info necessary to represent an instance in the
    dlplan library
    :param domain_lan: domain language from the tarski library (that can be read from PDDL files)
    :param add_goals: if true, for each predicate "p" an extra goal predicate "p_g" is added. This is done in Drexler
    et al.'s "Learning Sketches for Decomposing Planning Problems into Subproblems of Bounded Width" paper such that
    features can indicate when goal predicates are achieved
    :return: Vocabulary Info which contains all domain predicates
    """
    v = dlplan.core.VocabularyInfo()
    for p in domain_lan.predicates:
        if isinstance(p.name, str):
            v.add_predicate(str(p.name), p.arity, False)
            if add_goals:
                v.add_predicate(str(p.name) + '_g', p.arity, True)
    for c in domain_lan.constants():
        v.add_constant(c.name)
    return v


def dlinstance_from_tarski(domain: tarski.fstrips.Problem,
                           instance: tarski.fstrips.Problem) -> dlplan.core.InstanceInfo:
    """
    Translate a domain and its instance represented in a class from the Tarski library into an instance represented in
    the DLPlan library
    :param domain: A Tarski problem which was constructed by parsing a domain file
    :param instance: A Tarski problem which was constructed by parsing both a domain file and an instance of that domain
    :return: A DLPlan instance
    """
    v: dlplan.core.VocabularyInfo = dlvocab_from_tarski(domain.language)
    i = dlplan.core.InstanceInfo(v)
    d: dict[TSort, list[TConstant]] = sort_constants(instance.language)
    goal = instance.goal

    for p in domain.language.predicates:
        if isinstance(p.name, str):     # a tarski language contains some non-string predicates that are not used in the dlplan instances
            if not p.sort:
                i.add_atom(p.name, [])
            else:
                # TODO delete the on(b1, b1)
                combs: list[tuple[TConstant]] = typed_permutations(p.sort, d)
                for c in combs:
                    i.add_atom(p.name, [obj.name for obj in c])

    def add_goal(g):
        match g:
            case tarski.syntax.Atom():
                i.add_static_atom(g.predicate.name + '_g', [a.name for a in g.subterms])
            case tarski.syntax.CompoundFormula():
                match g.connective:
                    case tarski.syntax.Connective.And:
                        for s in g.subformulas: add_goal(s)
                    case _:
                        raise NotImplementedError(g.connective)
            case _:
                raise NotImplementedError

    add_goal(goal)
    return i
