# This file defines the TransitionSystem and GraphSystem classes

from src.transition_system.graph import DirectedGraph

StateStr = set[str]     # represent a state as a set of propositions (strings)


class TransitionSystem:
    """
    Representation of a transition system containing the graph of the system, the states that label the nodes of the
    graph, an initial state which is represented as the index of state in the states list, and the goal states which are
    also represented as indices.
    """
    states: list[StateStr]
    graph: DirectedGraph
    init: int
    goals: list[int]

    def __init__(self, states: list[StateStr], graph: DirectedGraph, init: int, goals: list[int]):
        self.states = states
        self.graph = graph
        self.init = init
        self.goals = goals

    @classmethod
    def deserialize(cls, data: dict) -> 'Self':
        """ Create TransitionSystem object from json readable object. Necessary for cashing."""
        assert("states" in data.keys())
        assert("graph" in data.keys())
        assert("init" in data.keys())
        assert("goals" in data.keys())
        graph = DirectedGraph(data["graph"])
        return cls([set(s) for s in data["states"]], graph, data["init"], data["goals"])

    def serialize(self) -> dict:
        """ Convert information from TransitionSystem object into a json readable object. Necessary for cashing."""
        return {"init": self.init, "goals": self.goals, "graph": self.graph.adj, "states": [list(s) for s in self.states]}


class GraphSystem:
    """
    A GraphSystem contains graph of a transition system, together with the ordered states that label the nodes of the
    graph.
    """
    states: list[StateStr]
    graph: DirectedGraph

    def __init__(self, states: list[StateStr], graph: DirectedGraph):
        self.states = states
        self.graph = graph

    @classmethod
    def deserialize(cls, data: dict):
        """ Create GraphSystem object from json readable object. Necessary for cashing."""
        assert("states" in data.keys())
        assert("graph" in data.keys())
        graph = DirectedGraph(data["graph"])
        return cls([set(s) for s in data["states"]], graph)

    def serialize(self) -> dict:
        """ Convert information from Graphsystem object into a json readable object. Necessary for cashing."""
        return {"graph": self.graph.adj, "states": [list(s) for s in self.states]}

