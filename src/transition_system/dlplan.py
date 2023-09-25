import dlplan
from dlplan.core import State as DLState
from typing import Union

from src.transition_system.transition_system import StateStr

DLFeature = Union[dlplan.core.Boolean, dlplan.core.Numerical]


def eval_feature(feature: DLFeature, states: set[DLState]) -> dict[DLState, any]:
    """
    Calculate the value of a feature for a set of states
    :param feature:
    :param states:
    :return: A dictionary with for each state the value of the feature in that state
    """
    return {s: feature.evaluate(s) for s in states}


def eval_features(features: list[DLFeature], states: list[DLState]) -> dict[DLFeature, dict[DLState, any]]:
    """
    Calculate the values features for a set of states
    :param features:
    :param states:
    :return: A dictionary with for each feature, for each state the value of that feature in that state
    """
    return {f: {s: f.evaluate(s) for s in states} for f in features}


def dlstate_from_state(state: StateStr, instance: dlplan.core.InstanceInfo) -> DLState:
    """
    Translate a state represented as a string into a DLPlan State object
    :param state: A state represented as a set of strings in which each string is a predicate
    :param instance: DLPlan instance info which contains all predicates of the instance
    :return: The same state as a DLPlan State object
    """
    return dlplan.core.State(instance, [instance.get_atom(atom) for atom in state])





