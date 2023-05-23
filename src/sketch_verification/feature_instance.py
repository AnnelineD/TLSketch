from typing import Union

import dlplan

from ..transition_system.graph import DirectedGraph


class FeatureInstance:
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
        return {f_name: (min(self.feature_valuations[f_name]), max(self.feature_valuations[f_name]))
                for f_name in self.feature_valuations.keys() if f_name.startswith('n_')}
