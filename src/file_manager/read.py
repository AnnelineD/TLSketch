from src.transition_system.graph import DirectedGraph
import json
import dlplan


# TODO make class for this???
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