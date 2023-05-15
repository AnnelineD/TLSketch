import json
import os.path
from typing import Union

import dlplan
from dlplan import State as DLState

from src.transition_system.transition_system import TransitionSystem


def transition_system(ts: TransitionSystem) -> dict:
    return {"init": ts.init, "goals": ts.goals, "graph": ts.graph.adj, "states": ts.states}

"""
def transition_system(graph: DirectedGraph, init: int, goal_states: list[int], file_path: str, override: bool = True):
    if os.path.isfile(file_path) and not override:
        return

    with open(file_path, "w") as trans_file:
        json.dump({"init": init, "goal": goal_states, "graph": graph.adj}, trans_file)
"""

"""
def dl_states(states: list[DLState], file_path: str, override: bool = True):
    if os.path.isfile(file_path) and not override:
        return

    assert (len(states) > 0)
    assert (all([s.get_instance_info() == states[0].get_instance_info()
                 for s in states]))  # all states come from the same instance

    with open(file_path, "w") as state_file:
        json.dump([[states[0].get_instance_info().get_atom(atom_idx).get_name()
                    for atom_idx in state.get_atom_idxs()]
                   for state in states], state_file)



def feature_representations(features: list[str], file_path: str):
    with open(file_path, "w") as f:
        json.dump(features, f)


def features(features: list[Union[dlplan.Numerical, dlplan.Boolean]], file_path: str):
    reprs = list(map(lambda x: x.compute_repr(), features))
    feature_representations(reprs, file_path)
"""


def feature_valuations(valuations: dict[str, Union[list[int], list[bool]]], file_path: str):
    with open(file_path, "w") as feature_file:
        json.dump(valuations, feature_file)
