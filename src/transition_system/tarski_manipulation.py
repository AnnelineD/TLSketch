# Methods that use and make objects from the tarski library
# There are no representations from other libraries used in this file

# import tarski
import tarski.search.operations
import itertools

from typing import List
from .types import *
from tarski.syntax.transform.action_grounding import ground_schema


def do_operator(schema: TAction, arguments: list[str], state: TModel) -> TModel:
    """
    Apply an action schema with given arguments to a state
    :param schema: An action schema
    :param arguments: The arguments to ground the action schema
    :param state: State to start from
    :return: New state obtained by applying the grounded action to the provided state
    """
    action = ground_schema(schema, arguments)
    return do_ground_action(action, state)


def do_ground_action(action: TAction, state: TModel) -> TModel:
    """
    Apply a ground action to a state
    :param action: A ground action
    :param state: A state to start from
    :return: State that results from applying the action to the provided state
    """
    if tarski.search.operations.is_applicable(state, action):
        return tarski.search.operations.progress(state, action)
    else:
        return state


def get_ground_action(schema: TAction, sorted_objects: dict[TSort, list[TConstant]]) -> List[TAction]:
    """
    Ground an action schema with given objects
    :param schema: Action schema
    :param sorted_objects: A dictionary with types as keys and a list of objects of the key type as values
    :return: All ground actions that can be made using the action schema and provided objects
    """
    perms = map(lambda perm: list(map(lambda p: p.name, perm)), typed_permutations(schema.sort(), sorted_objects))
    ground_actions = [ground_schema(schema, p) for p in perms]
    return ground_actions


def get_ground_actions(schemas: list[TAction], sorted_objects: dict[TSort, list[TConstant]]) -> list[TAction]:
    """
    Construct all grounded actions that can be made using the provided action schemas and objects
    :param schemas: A list of action schemas
    :param sorted_objects: A dictionary with types as keys and a list of objects of the key type as values
    :return: A list of ground actions
    """
    return [action for s in schemas for action in get_ground_action(s, sorted_objects)]


def typed_permutations(types: tuple[TSort], object_per_type: dict[TSort, list[TConstant]]) -> list[tuple[TConstant]]:
    """
    Given a list of types, return all combinations of objects that adhere to these types
    e.g. typed_permutations((loc, obj, obj), {loc: ["l1", "l2"], obj: ["o1", "o2"]})
        = [(l1, o1, o2), (l1, o2, o1), (l2, o1, o2), (l2, o2, o1)]
    :param types: tuple of types as tarski Sort objects
    :param object_per_type: A dictionary with types as keys and a list of objects of the key type as values
    :return: list of tuples that contain objects of the provided types
    """
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
    """
    Create a dictionary that sorts objects/constants per type/sort
    :param language: A first order language (of a problem instance)
    :return: A dictionary with types as keys and a list of objects of the key type as values
    """
    d = dict()
    for s in language.sorts:
        d[s] = [c for c in language.constants() if (c.sort == s) or (s in language.ancestor_sorts[c.sort])]
    return d


def has_params(action: TAction) -> bool:
    """
    Check whether an action is grounded
    :param action: A grounded action, action schema or partially-grounded action
    :return: True if the action still contains parameters, False if the action is fully grounded
    """
    return len(action.parameters.vars()) != 0

