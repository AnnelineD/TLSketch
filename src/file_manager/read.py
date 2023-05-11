from typing import Union

from src.sketch_verification.feature_instance import FeatureInstance
from src.transition_system.graph import DirectedGraph
from src.dlplan_utils import parse_features
import json
import dlplan

from src.transition_system.transition_system import TransitionSystem

"""
def transition_system(file_path) -> (DirectedGraph, int, list[int]):
    with open(file_path, "r") as f:
        data = json.load(f)
        init = data["init"]
        goal = data["goal"]
        adj = data["graph"]
    graph = DirectedGraph(adj)
    assert(init < graph.size())
    assert(g < graph.size() for g in goal)
    return DirectedGraph(adj), init, goal


def dl_states(file_path: str, instance: dlplan.InstanceInfo) -> list[dlplan.State]:
    with open(file_path, "r") as sf:
        data = json.load(sf)
    return [dlplan.State(instance, [instance.get_atom(instance.get_atom_idx(str(a))) for a in state]) for state in data]
"""


def transition_system(data: dict) -> TransitionSystem:
    assert("states" in data.keys())
    assert("graph" in data.keys())
    assert("init" in data.keys())
    assert("goals" in data.keys())
    return TransitionSystem(data["states"], data["graph"], data["init"], data["goals"])


def feature_representations(file_path: str) -> list[str]:
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def features(file_path: str, factory: dlplan.SyntacticElementFactory) -> (list[dlplan.Boolean], list[dlplan.Numerical]):
    feature_reps = feature_representations(file_path)
    return parse_features(feature_reps, factory)


def feature_valuations(file_path: str) -> dict[str, Union[list[int], list[bool]]]:
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def feature_instance(transition_path: str, valuation_path: str) -> FeatureInstance:
    graph, init, goals = transition_system(transition_path)
    valuations = feature_valuations(valuation_path)
    return FeatureInstance(graph, init, goals, valuations)

