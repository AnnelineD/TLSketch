from src.transition_system.graph import DirectedGraph

StateStr = set[str]


class TransitionSystem:
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
    def deserialize(cls, data: dict):
        assert("states" in data.keys())
        assert("graph" in data.keys())
        assert("init" in data.keys())
        assert("goals" in data.keys())
        graph = DirectedGraph(data["graph"])
        return cls([set(s) for s in data["states"]], graph, data["init"], data["goals"])

    def serialize(self) -> dict:
        return {"init": self.init, "goals": self.goals, "graph": self.graph.adj, "states": [list(s) for s in self.states]}


class GraphSystem:
    states: list[StateStr]
    graph: DirectedGraph

    def __init__(self, states: list[StateStr], graph: DirectedGraph):
        self.states = states
        self.graph = graph

    @classmethod
    def deserialize(cls, data: dict):
        assert("states" in data.keys())
        assert("graph" in data.keys())
        graph = DirectedGraph(data["graph"])
        return cls([set(s) for s in data["states"]], graph)

    def serialize(self) -> dict:
        return {"graph": self.graph.adj, "states": [list(s) for s in self.states]}

