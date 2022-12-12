
import tarski
from typing import List, Tuple, Dict, Set
from .types import *
import tarski.search
import itertools

from tarski.syntax.transform.action_grounding import ground_schema


def do_operator(schema: TAction, arguments: list[str], state: tarski.model.Model) -> tarski.model.Model:
    action = ground_schema(schema, arguments)
    return do_ground_action(action, state)


def do_ground_action(action: TAction, state: tarski.model.Model) -> tarski.model.Model:
    if tarski.search.operations.is_applicable(state, action):
        return tarski.search.operations.progress(state, action)
    else:
        return state


def get_ground_action(schema: TAction, sorted_objects: dict[TSort, list[TConstant]]) -> List[TAction]:
    perms = map(lambda perm: list(map(lambda p: p.name, perm)), typed_permutations(schema.sort(), sorted_objects))
    ground_actions = [ground_schema(schema, p) for p in perms]
    return ground_actions


def get_ground_actions(schemas: list[TAction], sorted_objects: dict[TSort, list[TConstant]]):
    """given action schemas and object, return all 'filled in' actions"""
    return [action for s in schemas for action in get_ground_action(s, sorted_objects)]


def typed_permutations(types: tuple[TSort], object_per_type: dict[TSort, list[TConstant]]) -> list[tuple[TConstant]]:
    if not types:
        return list(tuple())
    perms = list(itertools.product(*map(lambda t: object_per_type[t], types)))
    filtered_perms = list()  # filter all options where two times the same object is used
    for i, p in enumerate(perms):
        names = list(map(lambda x: x.name, p))  # use name representation of tarski Constants because equality is ill defined
        for n in names:
            if names.count(n) == 1:
                filtered_perms.append(p)  # we cannot delete elements from perms, since the equality between tarski Constants is ill defined
            break
    return filtered_perms


def sort_constants(language: tarski.fol.FirstOrderLanguage) -> dict[TSort, list[TConstant]]:
    d = dict()
    for s in language.sorts:
        d[s] = [c for c in language.constants() if c.sort == s]
    return d


def has_params(action: TAction) -> bool:
    return len(action.parameters.vars()) != 0

