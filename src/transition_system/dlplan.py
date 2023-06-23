import dlplan
from dlplan.core import State as DLState
from typing import Union

from src.transition_system.graph import DirectedGraph
from src.transition_system.transition_system import StateStr

Feature = Union[dlplan.core.Boolean, dlplan.core.Numerical]

"""
class DLTransitionModel:
    def __init__(self, instance_info: dlplan.InstanceInfo, states: list[dlplan.State], init: int, goal_state_indices: list[int], graph: DirectedGraph):
        for i, s in enumerate(states):
            assert(s.get_instance_info() == instance_info)
            s.set_index(i)
        self.initial_state = init
        self.graph = graph
        self.instance_info = instance_info
        self.states = states
        self.goal_states = goal_state_indices

    def add_features(self, features: list[Feature]):
        return DLFeatureTransitionModel(self, eval_features(features, self.states))


class DLFeatureTransitionModel:
    def __init__(self, model: DLTransitionModel, features: dict[Feature, dict[dlplan.State, Union[bool, int]]]):
        self.transition_model = model
        self.features: dict[Feature, dict[dlplan.State, Union[bool, int]]] = features

    def get_feature_bounds(self) -> dict[dlplan.Numerical, int]:
        bounds = dict[dlplan.Numerical, int]()
        for f, ss in self.features.items():
            if isinstance(f, dlplan.Numerical):
                vals: list[int] = [v for v in ss.values()]
                bounds.update({f: max(vals)})
        return bounds

"""
def eval_feature(feature, states: set[DLState]) -> dict[DLState, Feature]:
    return {s: feature.evaluate(s) for s in states}


def eval_features(features: list[Feature], states: list[DLState]) -> dict[Feature, dict[DLState, any]]:
    return {f: {s: f.evaluate(s) for s in states} for f in features}


def dlstate_from_state(state: StateStr, instance: dlplan.core.InstanceInfo) -> DLState:
    return dlplan.core.State(instance, [instance.get_atom(atom) for atom in state])





