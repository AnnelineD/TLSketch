import json
import os.path

from dlplan import State as DLState

from src.transition_system.graph import DirectedGraph


def transition_system(graph: DirectedGraph, init: int, goal_states: list[int], file_path: str, override: bool = True):
    if os.path.isfile(file_path) and not override:
        return

    with open(file_path, "w") as trans_file:
        json.dump({"init": init, "goal": goal_states, "graph": graph.adj}, trans_file)


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
