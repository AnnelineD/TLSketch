from src.transition_system.graph import DirectedGraph

StateStr = list[str]


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
