# Definition of the FeatureInstance class

from typing import Union
from ..transition_system.graph import DirectedGraph


class FeatureInstance:
    """ A domain instance with added features and all valuations of the features over the reachable states of the domain
    instance. Note: a FeatureInstance does not contain the reachable states themselves because the state descriptions
    are not necessary anymore once the feature evaluations are calculated.

    Attributes:
        graph           The transition system graph
        init            The index of the initial state (i.e. the number of the node in the graph)
        goal_states     The indices of the goal states
        feature_valuations  Dict with for each feature a list of its value in each state.
                            E.g. {'f1': [3, 2, 1], 'f2': [True, True, False]} means that for the state represented by
                            node 0 in the graph, feature 'f1'=3 and 'f2'=True. For node 1 we have resp. 2 and True etc.
    """
    graph: DirectedGraph
    init: int
    goal_states: list[int]
    feature_valuations: dict[str, list[Union[bool, int]]]

    def __init__(self, graph: DirectedGraph, init: int, goal_states: list[int], feature_valuations: dict[str, list[Union[bool, int]]]):
        self.graph = graph
        self.init = init
        self.goal_states = goal_states
        self.feature_valuations = feature_valuations

    def get_bounds(self) -> dict[str, (int, int)]:
        """
        For each numerical feature, calculate the highest and lowest value it can be.
        :return: A dict with for each feature a tuple (lowest value, highest value)
        """
        return {f_name: (min(self.feature_valuations[f_name]), max(self.feature_valuations[f_name]))
                for f_name in self.feature_valuations.keys() if f_name.startswith('n_')}
