import dlplan
from dlplan import State as DLState
import copy
from typing import Union

Feature = Union[dlplan.Boolean, dlplan.Numerical]


class DLTransitionModel:
    def __init__(self, instance_info: dlplan.InstanceInfo, states: set[dlplan.State], features=None):
        for s in states:
            assert(s.get_instance_info() == instance_info)
        self.instance_info = instance_info
        self.states = states
        self.features: dict[Feature, dict[dlplan.State, Union[bool, int]]] = features


def eval_feature(feature, states: set[DLState]):  # -> dict[DLState, feature]
    return {s: feature.evaluate(s) for s in states}


def eval_features(features: set[Feature], states: set[DLState]) -> dict[Feature, dict[DLState, any]]:
    return {f: {s: f.evaluate(s) for s in states} for f in features}


def add_features2(tm: DLTransitionModel, features: set[Feature]):
    return DLTransitionModel(tm.instance_info, tm.states, eval_features(features, tm.states))



